import copy
import json
import logging
import re
import time
from datetime import datetime

import requests
from dateutil.parser import parse
from folioclient import FolioClient
from requests import HTTPError


class TransactionResult(object):
    def __init__(self, was_successful: bool, successful_message: str, error_message: str,
                 migration_report_message: str):
        self.was_successful = was_successful
        self.successful_message = successful_message
        self.error_message = error_message
        self.migration_report_message = migration_report_message


class LegacyLoan(object):
    def __init__(self, legacy_loan_dict, row=0):
        # validate
        correct_headers = ["item_barcode", "patron_barcode", "due_date", "out_date", "renewal_count"]
        for prop in correct_headers:
            if prop not in legacy_loan_dict:
                raise ValueError(f'Row {row}. Required property {prop} missing from legacy loan.\n'
                                 f'Does your file have the required headers {", ".join(correct_headers)}?\n'
                                 f'Headers in legacy loan: \n{json.dumps(list(legacy_loan_dict.keys()), indent=4)}')
            if not legacy_loan_dict[prop]:
                raise ValueError(f"Row {row}. Required property {prop} empty from legacy loan")
        try:
            temp_date_due: datetime = parse(legacy_loan_dict["due_date"])
        except Exception as ee:
            raise ValueError(f'Row {row}. Could not parse {legacy_loan_dict["due_date"]} into a valid ISO date {ee}')
        try:
            temp_date_out: datetime = parse(legacy_loan_dict["out_date"])
        except Exception as ee:
            raise ValueError(f'Row {row}. Could not parse {legacy_loan_dict["out_date"]} into a valid ISO date {ee}')

        # good to go, set properties
        self.item_barcode = legacy_loan_dict["item_barcode"]
        self.patron_barcode = legacy_loan_dict["patron_barcode"]
        self.due_date = temp_date_due
        self.out_date = temp_date_out
        self.renewal_count = int(legacy_loan_dict["renewal_count"])


class CirculationHelper:

    def __init__(self, folio_client: FolioClient, service_point_id):
        self.folio_client = folio_client
        self.service_point_id = service_point_id

    def check_out_by_barcode_override_iris(self, legacy_loan: LegacyLoan):
        t0_function = time.time()
        data = {
            "itemBarcode": legacy_loan.item_barcode,
            "userBarcode": legacy_loan.patron_barcode,
            "loanDate": legacy_loan.out_date.isoformat(),
            "servicePointId": self.service_point_id,
            "overrideBlocks": {"itemNotLoanableBlock": {"dueDate": legacy_loan.due_date.isoformat()},
                               "patronBlock": {},
                               "itemLimitBlock":{},
                               "comment": "Migrated from legacy system"}
        }
        path = "/circulation/check-out-by-barcode"
        url = f"{self.folio_client.okapi_url}{path}"
        try:
            req = requests.post(url, headers=self.folio_client.okapi_headers, data=json.dumps(data))
            if req.status_code == 422:
                error_message_from_folio = json.loads(req.text)['errors'][0]['message']
                stat_message = error_message_from_folio
                error_message = error_message_from_folio
                if "has the item status" in error_message_from_folio:
                    stat_message = re.findall(r"(?<=has the item status\s).*(?=\sand cannot be checked out)",
                                              error_message_from_folio)[0]
                    error_message = f"{stat_message} for item with barcode {legacy_loan.item_barcode}"
                elif "No item with barcode" in error_message_from_folio:
                    error_message = f"No item with barcode {legacy_loan.item_barcode} in FOLIO"
                    stat_message = "Item barcode not in FOLIO"
                elif " find user with matching barcode" in error_message_from_folio:
                    error_message = f"No patron with barcode {legacy_loan.patron_barcode} in FOLIO"
                    stat_message = "Patron barcode not in FOLIO"
                logging.error(f"{error_message} Patron barcode: {legacy_loan.patron_barcode} Item Barcode:{legacy_loan.item_barcode}")
                return TransactionResult(False, None, error_message, f"Check out error: {stat_message}")
            elif req.status_code == 201:
                stats = (f"Successfully checked out by barcode"
                         # f"HTTP {req.status_code} {json.dumps(json.loads(req.text), indent=4)} "
                         )
                logging.info(f"{stats} (item barcode {legacy_loan.item_barcode}) in {(time.time() - t0_function):.2f}s")
                return TransactionResult(True, json.loads(req.text), None, stats)
            elif req.status_code == 204:
                stats = f"Successfully checked out by barcode"
                logging.info(f"{stats} (item barcode {legacy_loan.item_barcode}) {req.status_code}")
                return TransactionResult(True, None, None, stats)
            else:
                req.raise_for_status()
        except HTTPError as exception:
            logging.error(f"{req.status_code}\tPOST FAILED {url}\n\t{json.dumps(data)}\n\t{req.text}", exc_info=True)
            return TransactionResult(False, None, "5XX", f"Failed checkout http status {req.status_code}")

    def check_out_by_barcode_override_honeysuckle(self, legacy_loan: LegacyLoan):
        t0_function = time.time()
        loan_to_post = {
            "itemBarcode": legacy_loan.item_barcode,
            "userBarcode": legacy_loan.patron_barcode,
            "loanDate": legacy_loan.out_date.isoformat(),
            "comment": "Migrated loan from Voyager",
            "servicePointId": self.service_point_id,
            "dueDate": legacy_loan.due_date.isoformat()
        }
        checkout_path = "/circulation/override-check-out-by-barcode"
        checkout_url = f"{self.folio_client.okapi_url}{checkout_path}"
        try:
            req = requests.post(checkout_url, headers=self.folio_client.okapi_headers,
                                data=json.dumps(loan_to_post))
            if req.status_code == 422:
                error_message_from_folio = json.loads(req.text)['errors'][0]['message']
                stat_message = error_message_from_folio
                error_message = error_message_from_folio
                if "has the item status" in error_message_from_folio:
                    stat_message = re.findall(r"(?<=has the item status\s).*(?=\sand cannot be checked out)",
                                              error_message_from_folio)[0]
                    error_message = f"{stat_message} for item with barcode {legacy_loan.item_barcode}"
                elif "No item with barcode" in error_message_from_folio:
                    error_message = f"No item with barcode {legacy_loan.item_barcode} in FOLIO"
                    stat_message = "Item barcode not in FOLIO"
                elif " find user with matching barcode" in error_message_from_folio:
                    error_message = f"No patron with barcode {legacy_loan.patron_barcode} in FOLIO"
                    stat_message = "Patron barcode not in FOLIO"
                logging.error(f"{error_message} {legacy_loan.patron_barcode} {legacy_loan.item_barcode}")
                return TransactionResult(False, None, error_message, f"Check out error: {stat_message}")
            elif req.status_code == 201:
                stats = f"Successfully checked out by barcode ({req.status_code})"
                logging.info(stats)
                return TransactionResult(True, json.loads(req.text), None, stats)
            elif req.status_code == 204:
                stats = f"Successfully checked out by barcode ({req.status_code})"
                logging.info(stats)
                return TransactionResult(True, None, None, stats)
            else:
                req.raise_for_status()
        except HTTPError as exception:
            logging.error(
                f"{req.status_code}\tPOST FAILED {checkout_url}\n\t{json.dumps(loan_to_post)}\n\t{req.text}",
                exc_info=True)
            return TransactionResult(False, None, "5XX", f"Failed checkout http status {req.status_code}")

    @staticmethod
    def check_out_by_barcode(folio_client, item_barcode: str, patron_barcode: str, service_point_id: str):
        # TODO: add logging instead of print out
        t0_function = time.time()
        data = {
            "itemBarcode": item_barcode,
            "userBarcode": patron_barcode,
            "loanDate": datetime.now().isoformat(),
            "servicePointId": service_point_id,
        }
        path = "/circulation/check-out-by-barcode"
        url = f"{folio_client.okapi_url}{path}"
        try:
            req = requests.post(url, headers=folio_client.okapi_headers, data=json.dumps(data))
            if req.status_code == 422:
                error_message = json.loads(req.text)['errors'][0]['message']
                if "has the item status" in error_message:
                    error_message = re.findall(r"(?<=has the item status\s).*(?=\sand cannot be checked out)",
                                               error_message)[0]
                elif "No item with barcode" in error_message:
                    error_message = "Missing barcode"
                logging.error(error_message)
                return False, None, error_message, f"Check out error: {error_message}"
            elif req.status_code == 201:
                stats = f"Successfully checked out by barcode ({req.status_code})"
                logging.info(stats)
                return True, json.loads(req.text), None, stats
            elif req.status_code == 204:
                stats = f"Successfully checked out by barcode ({req.status_code})"
                logging.info(stats)
                return True, None, None, stats
            else:
                req.raise_for_status()
        except HTTPError as exception:
            logging.error(f"{req.status_code}\tPOST FAILED {url}\n\t{json.dumps(data)}\n\t{req.text}", exc_info=True)
            return False, None, "5XX", f"Failed checkout http status {req.status_code}"

    @staticmethod
    def create_request(
            folio_client: FolioClient, request_type, patron, item, service_point_id, request_date=datetime.now(),
    ):
        try:
            df = "%Y-%m-%dT%H:%M:%S.%f+0000"
            data = {
                "requestType": request_type,
                "fulfilmentPreference": "Hold Shelf",
                "requester": {"barcode": patron["barcode"]},
                "requesterId": patron["id"],
                "item": {"barcode": item["barcode"]},
                "itemId": item["id"],
                "pickupServicePointId": service_point_id,
                "requestDate": request_date.strftime(df),
            }
            path = "/circulation/requests"
            url = f"{folio_client.okapi_url}{path}"
            req = requests.post(url, headers=folio_client.okapi_headers, data=json.dumps(data))
            logging.debug(f"POST {req.status_code}\t{url}\t{json.dumps(data)}")
            if str(req.status_code) == "422":
                logging.error(f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(data)}")
                return False
            else:
                req.raise_for_status()
                logging.info(f"{req.status_code} Successfully created {request_type}")
                return True
        except Exception as exception:
            logging.error(exception, exc_info=True)
            return False

    @staticmethod
    def extend_open_loan(folio_client: FolioClient, loan, extension_due_date, extend_out_date):
        # TODO: add logging instead of print out
        try:
            df = "%Y-%m-%dT%H:%M:%S.%f+0000"
            loan_to_put = copy.deepcopy(loan)
            del loan_to_put["metadata"]
            loan_to_put["dueDate"] = extension_due_date.isoformat()
            loan_to_put["loanDate"] = extend_out_date.isoformat()
            url = f"{folio_client.okapi_url}/circulation/loans/{loan_to_put['id']}"

            req = requests.put(
                url, headers=folio_client.okapi_headers, data=json.dumps(loan_to_put)
            )
            logging.info(f"{req.status_code}\tPUT Extend loan {loan_to_put['id']} to {loan_to_put['dueDate']}\t {url}")
            if str(req.status_code) == "422":
                logging.error(f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(loan_to_put)}")
                return False
            else:
                req.raise_for_status()
                logging.info(f"{req.status_code} Successfully Extended loan")
            return True
        except Exception as exception:
            logging.error(f"PUT FAILED Extend loan to {loan_to_put['dueDate']}\t {url}\t{json.dumps(loan_to_put)}",
                          exc_info=True)
            return False

    @staticmethod
    def create_request(
            folio_client: FolioClient, request_type, patron, item, service_point_id, request_date=datetime.now(),
    ):
        try:
            df = "%Y-%m-%dT%H:%M:%S.%f+0000"
            data = {
                "requestType": request_type,
                "fulfilmentPreference": "Hold Shelf",
                "requester": {"barcode": patron["barcode"]},
                "requesterId": patron["id"],
                "item": {"barcode": item["barcode"]},
                "itemId": item["id"],
                "pickupServicePointId": service_point_id,
                "requestDate": request_date.strftime(df),
            }
            path = "/circulation/requests"
            url = f"{folio_client.okapi_url}{path}"
            req = requests.post(url, headers=folio_client.okapi_headers, data=json.dumps(data))
            logging.debug(f"POST {req.status_code}\t{url}\t{json.dumps(data)}")
            if str(req.status_code) == "422":
                logging.error(f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(data)}")
            else:
                req.raise_for_status()
                logging.info(f"POST {req.status_code} Successfully created request {request_type}")
        except Exception as exception:
            logging.error(exception, exc_info=True)
