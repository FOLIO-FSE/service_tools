import copy
import csv
import json
import time
import traceback
from abc import abstractmethod
import xml.etree.ElementTree as ET
from datetime import datetime as dt, datetime

import dateutil
import requests

from helpers.custom_dict import InsensitiveDictReader
from service_tasks.service_task_base import ServiceTaskBase


class MigrateOpenLoans(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.service_point_id = args.service_point_id
        csv.register_dialect("tsv", delimiter="\t")
        with open(args.open_loans_file) as loans_file:
            self.loans = list(InsensitiveDictReader(loans_file, dialect="tsv"))
        print(f"{len(self.loans)} loans to migrate")
        self.patron_item_combos = set()
        self.t0 = time.time()
        self.duplicate_loans = 0
        self.skipped_since_already_added = 0
        self.migration_report = {}
        self.processed_items = set()
        self.successful_items = set()
        self.failed = {}
        self.failed_and_not_dupe = {}
        print("Init completed")

    def do_work(self):
        print("Starting")
        i = 0
        for legacy_loan in self.loans[18:]:
            if legacy_loan["item_id"] not in self.successful_items:
                try:
                    t0_function = time.time()
                    i += 1
                    folio_loan = self.check_out_by_barcode(
                        legacy_loan["item_barcode"],
                        legacy_loan["patron_barcode"],
                        dt.now(),
                        self.service_point_id
                    )
                    # "extend" the loan date backwards in time in a randomized matter
                    if folio_loan[0]:
                        self.handle_previously_failed_loans(legacy_loan)
                        # extend loan backwards
                        if self.change_due_date(folio_loan[1], legacy_loan):
                            loan_to_extend = folio_loan[1]
                            due_date = dateutil.parser.isoparse(legacy_loan["due_date"])
                            out_date = dateutil.parser.isoparse(legacy_loan["out_date"])
                            renewal_count = legacy_loan["renewal_count"]

                            self.update_open_loan(
                                loan_to_extend, due_date, out_date, renewal_count
                            )
                            print(f"{timings(self.t0, t0_function, i)} {i}")
                            self.successful_items.add(legacy_loan["item_id"])
                    # Loan Posting Failed
                    else:
                        # First failure
                        if legacy_loan["item_id"] not in self.failed:
                            print(f"Adding loan to failed {legacy_loan}")
                            self.failed[legacy_loan["item_id"]] = (folio_loan, legacy_loan)
                        # Second Failure
                        else:
                            print(f"Loan already in failed {legacy_loan}")
                            self.failed_and_not_dupe[legacy_loan["item_id"]] = [
                                (folio_loan, legacy_loan),
                                self.failed[legacy_loan["item_id"]],
                            ]
                            self.duplicate_loans += 1
                            del self.failed[legacy_loan["item_id"]]
                except Exception as ee:
                    print(f"Error in row {i} {legacy_loan} {ee}")
                    ##raise ee
            else:
                print(f"loan already successfully processed {json.dumps(legacy_loan)}")
                self.skipped_since_already_added += 1
                self.duplicate_loans += 1
        # wrap up
        for k, v in self.failed.items():
            self.failed_and_not_dupe[k] = [v]
        print(json.dumps(self.failed_and_not_dupe, sort_keys=True, indent=4))
        print("## Loan migration counters")
        print("Title | Number")
        print("--- | ---:")
        print(f"Duplicate rows in file | {self.duplicate_loans}")
        print(f"Skipped since already added | {self.skipped_since_already_added}")
        print(f"Successfully checked out items | {len(self.successful_items)}")
        print(f"Failed items/loans | {len(self.failed_and_not_dupe)}")
        print(f"Total Rows in file  | {i}")
        for a in self.migration_report:
            print(f"# {a}")
            for b in self.migration_report[a]:
                print(b)

    def check_out_by_barcode(
            self, item_barcode, patron_barcode, loan_date: datetime, service_point_id
    ):
        # TODO: add logging instead of print out
        data = {
            "itemBarcode": item_barcode,
            "userBarcode": patron_barcode,
            "loanDate": loan_date.isoformat(),
            "servicePointId": service_point_id,
        }
        path = "/circulation/check-out-by-barcode"
        url = f"{self.folio_client.okapi_url}{path}"
        try:
            req = requests.post(url, headers=self.folio_client.okapi_headers, data=json.dumps(data))
            if str(req.status_code) == "422":
                print(
                    f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(data)}",
                    flush=True,
                )
                return False, None, json.loads(req.text)["errors"][0]["message"]
            elif str(req.status_code) == "201":
                print(f"{req.status_code}\tPOST {url}", flush=True)
                return True, json.loads(req.text), None
            else:
                req.raise_for_status()
        except Exception as exception:
            print(f"\tPOST FAILED {url}\t{json.dumps(data)}", flush=True)
            traceback.print_exc()
            print(exception, flush=True)
            return False, None, str(exception)

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

        api_url = f"{self.folio_client.okapi_url}/circulation/loans/{folio_loan['id']}/change-due-date"
        body = {"dueDate": dateutil.parser.isoparse(legacy_loan["due_date"]).isoformat()}
        req = requests.post(
            api_url, headers=self.folio_client.okapi_headers, data=json.dumps(body)
        )
        if str(req.status_code) == "422":
            error_message = json.loads(req.text)['errors'][0]['message']
            print(
                f"{error_message}\t",
                flush=True,
            )
            self.add_stats(error_message)
            return False
        else:
            req.raise_for_status()
        print(json.dumps(req.text))
        return True

    def update_open_loan(self, loan, extension_due_date, extend_out_date, renewal_count=0):
        # TODO: add logging instead of print out
        try:
            df = "%Y-%m-%dT%H:%M:%S.%f+0000"
            loan_to_put = copy.deepcopy(loan)
            del loan_to_put["metadata"]
            loan_to_put["dueDate"] = extension_due_date.isoformat()
            loan_to_put["loanDate"] = extend_out_date.isoformat()
            loan_to_put["renewalCount"] = renewal_count
            url = f"{self.folio_client.okapi_url}/circulation/loans/{loan_to_put['id']}"
            req = requests.put(
                url, headers=self.folio_client.okapi_headers, data=json.dumps(loan_to_put)
            )
            print(
                f"{req.status_code}\tPUT Extend loan {loan_to_put['id']} to {loan_to_put['dueDate']}\t {url}",
                flush=True,
            )
            if str(req.status_code) == "422":
                print(
                    f"{json.loads(req.text)['errors'][0]['message']}\t{json.dumps(loan_to_put)}",
                    flush=True,
                )
                return False
            else:
                req.raise_for_status()
            return True
        except Exception as exception:
            print(
                f"PUT FAILED Extend loan to {loan_to_put['dueDate']}\t {url}\t{json.dumps(loan_to_put)}",
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
