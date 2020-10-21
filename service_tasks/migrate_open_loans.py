import copy
import csv
import json
import re
import time
import traceback
from abc import abstractmethod
from datetime import datetime as dt, timedelta

import requests
from dateutil import parser as du_parser
from requests import HTTPError

from helpers.custom_dict import InsensitiveDictReader
from service_tasks.service_task_base import ServiceTaskBase


class MigrateOpenLoans(ServiceTaskBase):
    """Migrates Open Loans using the various Business logic apis for Circulation"""

    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.service_point_id = args.service_point_id
        csv.register_dialect("tsv", delimiter="\t")
        with open(args.open_loans_file, 'r') as loans_file:
            self.loans = list(InsensitiveDictReader(loans_file, dialect="tsv"))
        print(f"{len(self.loans)} loans to migrate", flush=True)
        self.patron_item_combos = set()
        self.t0 = time.time()
        self.num_duplicate_loans = 0
        self.skipped_since_already_added = 0
        self.processed_items = set()
        self.missing_barcodes = set()
        self.missing_patron_barcodes = set()
        self.successful_items = set()
        self.failed = {}
        self.num_legacy_loans_processed = 0
        self.failed_and_not_dupe = {}
        self.starting_point = 0  # TODO: Set as arg
        print("Init completed", flush=True)

    def do_work(self):
        print("Starting", flush=True)
        if self.starting_point > 0:
            print(f"Skipping {self.starting_point} records")

        for legacy_loan in self.loans[self.starting_point:]:
            self.num_legacy_loans_processed += 1
            if self.num_legacy_loans_processed % 25 == 0:
                self.print_dict_to_md_table(self.stats)
                print(
                    f"{timings(self.t0, t0_migration, self.num_legacy_loans_processed)} {self.num_legacy_loans_processed}",
                    flush=True)

            if self.is_processed(legacy_loan):
                continue  # no need to process
            t0_migration = time.time()
            try:
                res_checkout = self.check_out_by_barcode(legacy_loan, self.service_point_id)
                if not res_checkout[0]:
                    res_checkout = self.handle_checkout_failure(legacy_loan, res_checkout)
                    if not res_checkout[0]:
                        continue

                res_change_due_date = self.change_due_date(res_checkout[1], legacy_loan)
                if not res_change_due_date[0] and not self.handle_due_date_change_failure(legacy_loan,
                                                                                          res_change_due_date):
                    continue

                res_loan_update = self.update_open_loan(res_checkout[1], legacy_loan)
                if not res_loan_update[0]:
                    self.handle_loan_update_failure(legacy_loan, res_loan_update)
                    continue

                self.add_stats("Successfully migrated loans")

            except Exception as ee:  # Catch other exceptions than HTTP errors
                print(f"Error in row {self.num_legacy_loans_processed + 1} {legacy_loan} {ee}", flush=True)
                traceback.print_exc()
                # raise ee

        self.wrap_up()

    def wrap_up(self):
        # wrap up
        for k, v in self.failed.items():
            self.failed_and_not_dupe[k] = [v]
        # print(json.dumps(self.failed_and_not_dupe, sort_keys=True, indent=4))
        print(f"## Missing item barcodes ({len(self.missing_barcodes)})")
        print(json.dumps(list(self.missing_barcodes)))
        print(f"## Missing patron barcodes ({len(self.missing_patron_barcodes)})")
        print(json.dumps(list(self.missing_patron_barcodes)))
        print("## Loan migration counters")
        print("Title | Number")
        print("--- | ---:")
        print(f"Failed items/loans | {len(self.failed_and_not_dupe)}")
        print(f"Total Rows in file  | {self.num_legacy_loans_processed}")
        super().wrap_up()

    def is_processed(self, legacy_loan):
        if legacy_loan["item_id"] not in self.successful_items:
            return False
        else:
            self.add_stats("Item has already been processed")
            return True

    def handle_checkout_failure(self, legacy_loan, folio_checkout):
        if folio_checkout[2] == "5XX":
            return False, None, None
        if folio_checkout[2] == "Could not find user with matching barcode":
            self.missing_patron_barcodes.add(legacy_loan["patron_barcode"])
            return False, None, None
        elif folio_checkout[2] == "Missing item barcode":
            self.missing_barcodes.add(legacy_loan["item_barcode"])
            return False, None, None
        elif folio_checkout[2] == "Declared lost":
            self.set_item_as_available(legacy_loan)
            res = self.check_out_by_barcode(legacy_loan, self.service_point_id)  # checkout_and_update
            if res[0]:
                self.declare_lost(res[1])
                self.add_stats("Handled Declared lost items")
            else:
                self.add_stats(f"Checkout failed when declaring as lost because: {res[2]}")
                raise Exception(f"Checkout failed when declaring as lost because: {res[2]}")
            return res
        elif folio_checkout[2] == "Cannot check out to inactive user":
            user = self.get_user_by_barcode(legacy_loan["patron_barcode"])
            expiration_date = user.get("expirationDate", dt.isoformat(dt.now()))
            user["expirationDate"] = dt.isoformat(dt.now() + timedelta(days=1))
            self.activate_user(user)
            res = self.check_out_by_barcode(legacy_loan, self.service_point_id)  # checkout_and_update
            self.deactivate_user(user, expiration_date)
            self.add_stats("Handled expired users")
            return res
        else:
            self.add_stats(f"Other checkout failure: {folio_checkout[2]}")
            # First failure. Add to list of failed loans
            if legacy_loan["item_id"] not in self.failed:
                self.failed[legacy_loan["item_id"]] = legacy_loan

            # Second Failure. For duplicate rows. Needs cleaning...
            else:
                print(f"Loan already in failed {legacy_loan}", flush=True)
                self.failed_and_not_dupe[legacy_loan["item_id"]] = [
                    legacy_loan,
                    self.failed[legacy_loan["item_id"]],
                ]
                self.add_stats("Duplicate loans")
                del self.failed[legacy_loan["item_id"]]
            return False, None, None

    def check_out_by_barcode(self, legacy_loan, service_point_id):
        # TODO: add logging instead of print out
        t0_function = time.time()
        data = {
            "itemBarcode": legacy_loan["item_barcode"],
            "userBarcode": legacy_loan["patron_barcode"],
            "loanDate": dt.now().isoformat(),
            "servicePointId": service_point_id,
        }
        path = "/circulation/check-out-by-barcode"
        url = f"{self.folio_client.okapi_url}{path}"
        try:
            req = requests.post(url, headers=self.folio_client.okapi_headers, data=json.dumps(data))
            if req.status_code == 422:
                error_message = json.loads(req.text)['errors'][0]['message']
                if "has the item status" in error_message:
                    error_message = re.findall("(?<=has the item status\s).*(?=\sand cannot be checked out)",
                                               error_message)[0]
                elif "No item with barcode" in error_message:
                    error_message = "Missing barcode"
                self.add_stats(f"Check out error: {error_message}")
                return False, None, error_message
            elif req.status_code == 201:
                self.add_stats(f"Successfully checked out by barcode ({req.status_code})")
                return True, json.loads(req.text), None
            elif req.status_code == 204:
                self.add_stats(f"Successfully checked out by barcode ({req.status_code})")
                return True, None, None
            else:
                self.add_stats(f"Failed checkout http status {req.status_code}")
                req.raise_for_status()
        except HTTPError as exception:
            print(f"{req.status_code}\tPOST FAILED {url}\n\t{json.dumps(data)}\n\t{req.text}", flush=True)
            print(exception, flush=True)
            return False, None, "5XX"

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,
                                     "open_loans_file", help="File to TSV file containing Open Loans",
                                     widget="FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser, "service_point_id", "Id of the service point where checkout occurs", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser,
                                         "open_loans_file", help="File to TSV file containing Open Loans")
        ServiceTaskBase.add_cli_argument(parser, "service_point_id", "Id of the service point where checkout occurs")

    def handle_previously_failed_loans(self, loan):
        if loan["item_id"] in self.failed:
            print(
                f"Loan succeeded but failed previously. Removing from failed {loan}"
            )
            # this loan har previously failed. It can now be removed from failures:
            del self.failed[loan["item_id"]]

    def change_due_date(self, folio_loan, legacy_loan):
        try:
            t0_function = time.time()
            api_url = f"{self.folio_client.okapi_url}/circulation/loans/{folio_loan['id']}/change-due-date"
            body = {"dueDate": du_parser.isoparse(str(legacy_loan["due_date"])).isoformat()}
            req = requests.post(
                api_url, headers=self.folio_client.okapi_headers, data=json.dumps(body)
            )
            if req.status_code == 422:
                error_message = json.loads(req.text)['errors'][0]['message']
                self.add_stats(f"Change due date error: {error_message}")
                print(
                    f"{error_message}\t",
                    flush=True,
                )
                self.add_stats(error_message)
                return False
            elif req.status_code == 201:
                self.add_stats(f"Successfully changed due date ({req.status_code})")
                return True, json.loads(req.text), None
            elif req.status_code == 204:
                self.add_stats(f"Successfully changed due date ({req.status_code})")
                return True, None, None
            else:
                self.add_stats(f"Update open loan error http status: {req.status_code}")
                req.raise_for_status()
        except HTTPError as exception:
            print(
                f"{req.status_code} POST FAILED Change Due Date to {api_url}\t{json.dumps(body)}",
                flush=True,
            )
            traceback.print_exc()
            print(exception, flush=True)
            return False, None, None

    def update_open_loan(self, folio_loan, legacy_loan):
        due_date = du_parser.isoparse(str(legacy_loan["due_date"]))
        out_date = du_parser.isoparse(str(legacy_loan["out_date"]))
        renewal_count = legacy_loan["renewal_count"]
        # TODO: add logging instead of print out
        t0_function = time.time()
        try:
            loan_to_put = copy.deepcopy(folio_loan)
            del loan_to_put["metadata"]
            loan_to_put["dueDate"] = due_date.isoformat()
            loan_to_put["loanDate"] = out_date.isoformat()
            loan_to_put["renewalCount"] = renewal_count
            url = f"{self.folio_client.okapi_url}/circulation/loans/{loan_to_put['id']}"
            req = requests.put(
                url, headers=self.folio_client.okapi_headers, data=json.dumps(loan_to_put)
            )
            if req.status_code == 422:
                error_message = json.loads(req.text)['errors'][0]['message']
                self.add_stats(f"Update open loan error: {error_message}")
                return False
            elif req.status_code == 201:
                self.add_stats(f"Successfully updated open loan ({req.status_code})")
                return True, json.loads(req.text), None
            elif req.status_code == 204:
                self.add_stats(f"Successfully updated open loan ({req.status_code})")
                return True, None, None
            else:
                self.add_stats(f"Update open loan error http status: {req.status_code}")
                req.raise_for_status()
            return True
        except HTTPError as exception:
            print(
                f"{req.status_code} PUT FAILED Extend loan to {loan_to_put['dueDate']}\t {url}\t{json.dumps(loan_to_put)}",
                flush=True,
            )
            traceback.print_exc()
            print(exception, flush=True)
            return False, None, None

    def handle_due_date_change_failure(self, legacy_loan, param):
        raise NotImplementedError()

    def handle_loan_update_failure(self, legacy_loan, param):
        raise NotImplementedError

    def declare_lost(self, folio_loan):
        declare_lost_url = f"/circulation/loans/{folio_loan['id']}/declare-item-lost"
        print(f"Declare lost url:{declare_lost_url}")
        due_date = du_parser.isoparse(folio_loan['dueDate'])
        data = {"declaredLostDateTime": dt.isoformat(due_date + timedelta(days=1)),
                "comment": "Created at migration. Date is due date + 1 day",
                "servicePointId": str(self.service_point_id)}
        print(f"Declare lost data: {json.dumps(data)}")
        self.folio_put_post(declare_lost_url, data, "POST", "Declare item as lost")
        self.stats("Successfully declared loan as lost")
        # TODO: Exception handling

    def set_item_as_available(self, legacy_loan):
        # Get Item by barcode, update status.
        item_url = f'{self.folio_client.okapi_url}/item-storage/items?query=(barcode=="{legacy_loan["item_barcode"]}")'
        resp = requests.get(item_url, headers=self.folio_client.okapi_headers)
        resp.raise_for_status()
        data = resp.json()
        folio_item = data["items"][0]
        folio_item["status"]["name"] = "Available"
        self.update_item(folio_item)
        self.add_stats("Successfully set item to Available")
        # TODO: Exception handling

    def activate_user(self, user):
        user["active"] = True
        self.update_user(user)
        self.add_stats("Successfully activated user")

    def deactivate_user(self, user, expiration_date):
        user["expirationDate"] = expiration_date
        user["active"] = False
        self.update_user(user)
        self.add_stats("Successfully deactivated user")

    def update_item(self, item):
        url = f'/item-storage/items/{item["id"]}'
        self.folio_put_post(url, item, "PUT", "Update item")

    def update_user(self, user):
        url = f'/users/{user["id"]}'
        self.folio_put_post(url, user, "PUT", "Update user")

    def get_user_by_barcode(self, barcode):
        url = f'{self.folio_client.okapi_url}/users?query=(barcode=="{barcode}")'
        resp = requests.get(url, headers=self.folio_client.okapi_headers)
        resp.raise_for_status()
        data = resp.json()
        return data["users"][0]

    def folio_put_post(self, url, data_dict, verb, action_description=""):
        full_url = f'{self.folio_client.okapi_url}{url}'
        try:
            if verb == "PUT":
                resp = requests.put(full_url, headers=self.folio_client.okapi_headers, data=json.dumps(data_dict))
            elif verb == "POST":
                resp = requests.post(full_url, headers=self.folio_client.okapi_headers, data=json.dumps(data_dict))
            else:
                raise Exception("Bad verb")
            if resp.status_code == 422:
                error_message = json.loads(resp.text)['errors'][0]['message']
                self.add_stats(f"{action_description} error: {error_message}")
                resp.raise_for_status()
            elif resp.status_code == 201:
                self.add_stats(f"Successfully {action_description} ({resp.status_code})")
            elif resp.status_code == 204:
                self.add_stats(f"Successfully {action_description} ({resp.status_code})")
            else:
                self.add_stats(f"{action_description} error. http status: {resp.status_code}")
                resp.raise_for_status()
            return True
        except HTTPError as exception:
            print(
                f"{resp.status_code}. {verb} FAILED for {url}",
                flush=True,
            )
            traceback.print_exc()
            print(exception, flush=True)
            return False


def timings(t0, t0func, num_objects):
    avg = num_objects / (time.time() - t0)
    elapsed = time.time() - t0
    elapsed_func = time.time() - t0func
    return (f"Total objects: {num_objects}\tTotal elapsed: {elapsed:.2f}\t"
            f"Average per object: {avg:.2f}\tElapsed this time: {elapsed_func:.2f}")
