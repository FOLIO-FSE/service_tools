import csv
import csv
import json
import logging
import time
import traceback
import uuid
from abc import abstractmethod

import requests
from requests import HTTPError

from helpers.circulation_helper import LegacyFeeFine
from helpers.custom_dict import InsensitiveDictReader
from service_tasks.service_task_base import ServiceTaskBase


class MigrateFeesAndFines(ServiceTaskBase):
    """Migrates fees and fines
    """

    def __init__(self, folio_client, args):
        super().__init__(folio_client)

        csv.register_dialect("tsv", delimiter="\t")
        self.valid_legacy_fees = []
        with open(args.fees_file, 'r') as fees_file:
            self.valid_legacy_fees = list(
                self.load_and_validate_legacy_fees(InsensitiveDictReader(fees_file, dialect="tsv")))
            logging.info(f"Loaded and validated {len(self.valid_legacy_fees)} fees in file")
        self.t0 = time.time()
        self.num_duplicate_loans = 0
        self.skipped_since_already_added = 0
        self.processed_items = set()
        self.failed = {}
        self.num_legacy_loans_processed = 0
        self.failed_and_not_dupe = {}

        self.starting_point = 0  # TODO: Set as arg
        logging.info("Init completed")

    def do_work(self):
        logging.info("Starting")

        if self.starting_point > 0:
            logging.info(f"Skipping {self.starting_point} records")

        for num_fees, legacy_fee in enumerate(self.valid_legacy_fees[self.starting_point:]):
            fee_fine_owner_name = "CUL"
            fee_fine_owner_id = "9898dd87-43dc-4c2b-ae55-2d8b66eb32ee"
            lost_fee_fine = "cf238f9f-7018-47b7-b815-bb2db798e19f"
            t0_migration = time.time()
            try:
                # Get item, by barcode
                item_path = f"/inventory/items?query=barcode=={legacy_fee.item_barcode}"
                logging.info(item_path)
                item = self.folio_client.folio_get(item_path, "items")[0]

                user_path = f"/users?query=barcode=={legacy_fee.patron_barcode}"
                logging.info(user_path)
                user = self.folio_client.folio_get(user_path, "users")[0]

                # Post this: /accounts
                account_id = str(uuid.uuid4())
                post_account_path = f"{self.folio_client.okapi_url}/accounts"
                account_payload = {
                    "amount": legacy_fee.amount,
                    "remaining": legacy_fee.remaining,
                    "status": {
                        "name": "Open"  # values used are Open and Closed
                    },
                    "paymentStatus": {
                        "name": "Outstanding"
                        # Outstanding, Paid partially, Paid fully, Waived partially, Waived fully, Transferred partially, Transferred fully, Refunded partially, Refunded fully, Cancelled as error
                    },
                    "feeFineType": type_map(legacy_fee.fee_fine_type)[1],
                    "feeFineOwner": fee_fine_owner_name,
                    "title": item.get("title", ""),
                    "callNumber": item.get("callNumber", ""),
                    "barcode": item.get("barcode", ""),
                    "materialType": item.get("materialType", {}).get("name", ""),
                    "location": item.get("effectiveLocation", {}).get("name", ""),
                    "metadata": self.folio_client.get_metadata_construct(),
                    "userId": user.get("id", ""),
                    "itemId": item.get("id", ""),
                    "materialTypeId": item.get("materialType", {}).get("id", ""),
                    "feeFineId": type_map(legacy_fee.fee_fine_type)[0],
                    "ownerId": fee_fine_owner_id,
                    "id": account_id
                }
                logging.info(json.dumps(account_payload))
                self.post_stuff(post_account_path, account_payload, legacy_fee.source_dict)

                # Post this to /feefineactions?query=(userId==895412c6-62b4-4680-bdcf-7c875f11dd5b)&limit=10000
                fee_fine_action_path = f"{self.folio_client.okapi_url}/feefineactions?query=(userId=={user['id']})&limit=10000"
                feefine_action_payload = {
                    "dateAction": legacy_fee.created_date.isoformat(),
                    "typeAction": type_map(legacy_fee.fee_fine_type)[1],
                    "comments": stringify_source_record(legacy_fee.source_dict),
                    "notify": False,  # For sure
                    "amountAction": legacy_fee.amount,
                    "balance": legacy_fee.remaining,
                    "transactionInformation": "",
                    "createdAt": "0e1de5af-8fc2-44e8-8aec-246dbea9c09b",
                    "source": self.folio_client.username,
                    "accountId": account_id,
                    "userId": user.get("id", ""),
                    "id": str(uuid.uuid4())
                }
                print("Feefine action payload")
                logging.info(json.dumps(feefine_action_payload))
                self.post_stuff(fee_fine_action_path, feefine_action_payload, legacy_fee.source_dict)
            except Exception as ee:  # Catch other exceptions than HTTP errors
                logging.info(f"Error in row {num_fees}  Item id: {legacy_fee.item_barcode}"
                             f"Patron id: {legacy_fee.patron_barcode} {ee}")
                traceback.print_exc()
                raise ee

        self.wrap_up()

    def post_stuff(self, request_path:str, payload: dict, source_data: dict):
        try:
            resp = requests.post(
                request_path, headers=self.folio_client.okapi_headers, data=json.dumps(payload)
            )
            logging.info(
                f"HTTP {resp.status_code} {request_path} {json.dumps(source_data)}")
            resp.raise_for_status()
        except HTTPError as httpError:
            logging.error(httpError)
            logging.info(resp.text)


    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,
                                     "fees_file", help="File to TSV file containing Open Loans",
                                     widget="FileChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser,
                                         "fees_file", help="File to TSV file containing Open Loans")

    @staticmethod
    def load_and_validate_legacy_fees(fees_reader):
        barcodes = set()
        duplicate_barcodes = set()
        logging.info("Validating legacy loans in file...")
        for legacy_fees_count, legacy_fee_dict in enumerate(fees_reader):
            yield LegacyFeeFine(legacy_fee_dict, legacy_fees_count)
        logging.info("Done validating legacy FeeFines")

    def wrap_up(self):
        # wrap up
        for k, v in self.failed.items():
            self.failed_and_not_dupe[k] = [v]
        logging.info("## Loan migration counters")
        logging.info("Title | Number")
        logging.info("--- | ---:")
        logging.info(f"Failed items/loans | {len(self.failed_and_not_dupe)}")
        logging.info(f"Total Rows in file  | {self.num_legacy_loans_processed}")
        super().wrap_up()


def timings(t0, t0func, num_objects):
    avg = num_objects / (time.time() - t0)
    elapsed = time.time() - t0
    elapsed_func = time.time() - t0func
    return (f"Total objects: {num_objects}\tTotal elapsed: {elapsed:.2f}\t"
            f"Average per object: {avg:.2f}\tElapsed this time: {elapsed_func:.2f}")


def stringify_source_record(legacy_fee):
    ret_str = ""
    for key, value in legacy_fee.items():
        ret_str += f"{key}: {value}\n"
    return ret_str


def type_map(type_code):
    m = {
        "": "",
        "1": ("9523cb96-e752-40c2-89da-60f3961a488d", "Overdue fine"),  # Overdue
        "2": ("6c6d86d1-f3af-42a1-8d3a-86df9a4c8408", "Lost item replacement"),  # Lost Item Replacement
        "3": ("c7dede15-aa48-45ed-860b-f996540180e0", "Lost item processing fee"),  # Lost Item Processing
        "4": ("", ""),  # Media Booking Late Charge
        "5": ("", ""),  # Media Booking Usage Fee
        "6": ("6c6d86d1-f3af-42a1-8d3a-86df9a4c8408", "Lost item replacement"),  # Equipment Replacement
        "7": ("c7dede15-aa48-45ed-860b-f996540180e0", "Lost item processing fee"),  # Lost Equipment Processing
        "8": ("", ""),  # Accrued Fine
        "9": ("", ""),  # Accrued Demerit
        "10": ("", ""),  # Demerit
        "11": ("", ""),  # Recall
        "12": ("fce8f9e1-8e1d-4457-bda1-e85d4854a734", "Damaged"),  # Damage & Repair Charge
        "13": ("", ""),  # Binding Charge
        "14": ("", ""),  # Miscellaneous Charge
        "15": ("", ""),  # Added by Fee Load
        "16": ("", ""),  # Added by Fee Load
        "17": ("", ""),  # Added by Fee Load
        "18": ("", ""),  # Added by Fee Load
        "19": ("", ""),  # Added by Fee Load
        "20": ("", "")  # Added by Fee Load
    }
    return m[type_code]


"""
{
  "feefines" : [ {
    "automatic" : true,
    "feeFineType" : "Overdue fine",
    "id" : "9523cb96-e752-40c2-89da-60f3961a488d"
  }, {
    "automatic" : true,
    "feeFineType" : "Replacement processing fee",
    "id" : "d20df2fb-45fd-4184-b238-0d25747ffdd9"
  }, {
    "automatic" : true,
    "feeFineType" : "Lost item fee",
    "id" : "cf238f9f-7018-47b7-b815-bb2db798e19f"
  }, {
    "automatic" : true,
    "feeFineType" : "Lost item processing fee",
    "id" : "c7dede15-aa48-45ed-860b-f996540180e0"
  }, {
    "automatic" : false,
    "feeFineType" : "Damaged",
    "ownerId" : "9898dd87-43dc-4c2b-ae55-2d8b66eb32ee",
    "metadata" : {
      "createdDate" : "2021-04-29T17:34:11.744+00:00",
      "createdByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc",
      "updatedDate" : "2021-04-29T17:34:11.744+00:00",
      "updatedByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc"
    },
    "id" : "fce8f9e1-8e1d-4457-bda1-e85d4854a734"
  }, {
    "automatic" : false,
    "feeFineType" : "Library card",
    "ownerId" : "9898dd87-43dc-4c2b-ae55-2d8b66eb32ee",
    "metadata" : {
      "createdDate" : "2021-04-29T17:34:39.316+00:00",
      "createdByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc",
      "updatedDate" : "2021-04-29T17:34:39.316+00:00",
      "updatedByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc"
    },
    "id" : "4e30d2ba-d90d-4ab4-bbc6-cea7e01427d4"
  }, {
    "automatic" : false,
    "feeFineType" : "Lost item replacement",
    "ownerId" : "9898dd87-43dc-4c2b-ae55-2d8b66eb32ee",
    "metadata" : {
      "createdDate" : "2021-04-29T17:34:48.160+00:00",
      "createdByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc",
      "updatedDate" : "2021-04-29T17:34:48.160+00:00",
      "updatedByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc"
    },
    "id" : "6c6d86d1-f3af-42a1-8d3a-86df9a4c8408"
  }, {
    "automatic" : false,
    "feeFineType" : "Overdue",
    "ownerId" : "9898dd87-43dc-4c2b-ae55-2d8b66eb32ee",
    "metadata" : {
      "createdDate" : "2021-04-29T17:34:54.040+00:00",
      "createdByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc",
      "updatedDate" : "2021-04-29T17:34:54.040+00:00",
      "updatedByUserId" : "a2959cda-1338-40ba-ad9e-368fc4cbf1cc"
    },
    "id" : "ea0923bd-1ba4-485a-a494-73e86ba260b5"
  }, {
    "automatic" : true,
    "feeFineType" : "Lost item fee (actual cost)",
    "id" : "73785370-d3bd-4d92-942d-ae2268e02ded"
  } ],
  "totalRecords" : 9,
  "resultInfo" : {
    "totalRecords" : 9,
    "facets" : [ ],
    "diagnostics" : [ ]
  }"""
