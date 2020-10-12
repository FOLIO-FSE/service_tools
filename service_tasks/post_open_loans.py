import argparse
import collections
import copy
import csv
import hashlib
import itertools
import json
import pathlib
import random
import time
import traceback
import uuid
import xml
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta
import json
import time
from abc import abstractmethod

import requests
from folioclient import FolioClient
import dateutil.parser
import requests
from service_tasks.service_task_base import ServiceTaskBase


class PostOpenLoans(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.skip = 0  # args.skip
        self.objects_file_path = args.objects_file_path
        self.num_rows = 0
        self.failed_posts = 0
        self.patron_item_combos = set()
        self.t0 = time.time()
        self.duplicate_loans = 0
        self.skipped_since_already_added = 0
        self.migration_report = {}
        self.processed_items = set()
        self.successful_items = set()
        self.failed = {}
        self.service_point_id = args.service_point_id
        self.failed_and_not_dupe = {}

    def do_work(self):
        csv.register_dialect("tsv", delimiter="\t")
        with open(self.objects_file_path) as loans_file:
            print("Starting....")
            i = 0
            loans = list(csv.DictReader(loans_file, dialect="tsv"))
            first = True
            for loan in loans:
                if first and not all(l for l in loans if l in ['item_barcode', "patron_barcode", 'item_id']):
                    first = False
                    missing = [l for l in loans if l not in ['item_barcode', "patron_barcode", 'item_id']]
                    raise Exception(f"Missing header(s) in file:\t{missing}")
                if loan["item_id"] not in self.successful_items:
                    try:
                        self.num_rows += 1
                        t0_function = time.time()
                        i += 1
                        loan_created = self.folio_client.check_out_by_barcode(
                            loan["item_barcode"],
                            loan["patron_barcode"],
                            dt.now(),
                            self.service_point_id,
                        )
                        # "extend" the loan date backwards in time in a randomized matter
                        if loan_created[0]:
                            # handle previously failed loans
                            if loan["item_id"] in self.failed:
                                print(
                                    f"Loan succeeded but failed previously. Removing from failed {loan}"
                                )
                                # this loan har previously failed. It can now be removed from failures:
                                del self.failed[loan["item_id"]]

                            # extend loan
                            loan_to_extend = loan_created[1]
                            due_date = dateutil.parser.isoparse(loan["due_date"])
                            out_date = dateutil.parser.isoparse(loan["out_date"])
                            self.folio_client.extend_open_loan(
                                loan_to_extend, due_date, out_date
                            )
                            print(f"{timings(self.t0, t0_function, i)}")
                            self.successful_items.add(loan["item_id"])
                        # Loan Posting Failed
                        else:
                            # First failure
                            if loan["item_id"] not in self.failed:
                                print(f"Adding loan to failed {loan}")
                                self.failed[loan["item_id"]] = (loan_created, loan)
                            # Second Failure
                            else:
                                print(f"Loan already in failed {loan}")
                                self.failed_and_not_dupe[loan["item_id"]] = [
                                    (loan_created, loan),
                                    self.failed[loan["item_id"]],
                                ]
                                self.duplicate_loans += 1
                                del self.failed[loan["item_id"]]

                    except Exception as ee:
                        print(f"Errror in row {i} {ee}")
                        raise ee
                else:
                    print(f"loan already successfully processed {json.dumps(loan)}")
                    self.skipped_since_already_added += 1
                    self.duplicate_loans += 1
            # wrap up
            for k, v in self.failed.items():
                self.failed_and_not_dupe[k] = [v]
            print(json.dumps(self.failed_and_not_dupe, sort_keys=True, indent=4))
            print("# Loan migration")
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

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "objects_file_path", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(parser, "service_point_id", "UUID of the service point that checked the items out",
                                     "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "objects_file_path", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "service_point_id", "UUID of the service point"
                                                                     "that checked the items out")


def timings(t0, t0func, num_objects):
    avg = num_objects / (time.time() - t0)
    elapsed = time.time() - t0
    elapsed_func = num_objects / (time.time() - t0func)
    return (f"Objects processed: {num_objects}\tTotal elapsed: {elapsed}\tAverage per object: {avg:.2f}\t"
            "Elapsed this time: {elapsed_func:.2f}")
