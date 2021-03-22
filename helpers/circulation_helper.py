import copy
import json
import logging
import re
import time
import traceback
from datetime import datetime as datetime
import requests
from folioclient import FolioClient
from requests import HTTPError


class CirculationHelper:

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
            logging.Error(f"{req.status_code}\tPOST FAILED {url}\n\t{json.dumps(data)}\n\t{req.text}", exc_info=True)
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
            logging.info(f"POST {req.status_code}\t{url}\t{json.dumps(data)}")
            if str(req.status_code) == "422":
                logging.error(f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(data)}")
                return False
            else:
                # print(req.text)
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
            return True
        except Exception as exception:
            logging.error(f"PUT FAILED Extend loan to {loan_to_put['dueDate']}\t {url}\t{json.dumps(loan_to_put)}", exc_info=True)
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
            logging.info(f"POST {req.status_code}\t{url}\t{json.dumps(data)}")
            if str(req.status_code) == "422":
                logging.error(f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(data)}")
            else:
                req.raise_for_status()
        except Exception as exception:
            logging.error(exception, exc_info=True)
