import csv
import json
import logging
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class SMCVTUpdateActiceBarcodes(ServiceTaskBase):
    def __init__(self, folio_client, args):
        csv.register_dialect("tsv", delimiter="\t")
        super().__init__(folio_client, "", args.results_folder)
        self.instance_ids = []
        self.args = args

    def do_work(self):
        api_path = "/item-storage/items"
        with open(self.args.input_file, "r", encoding="utf-8") as input_file:
            barcodes = {}
            # Set up combos
            for idx, row in enumerate(csv.DictReader(input_file, dialect="tsv")):
                if row["ITEM_ID"] not in barcodes:
                    self.add_stats("Unique items")
                    barcodes[row["ITEM_ID"]] = {"active": "", "inactive": ""}

                if row["BARCODE_STATUS_DESC"] == "Active":
                    barcodes[row["ITEM_ID"]]["active"] = row["ITEM_BARCODE"]
                elif row["BARCODE_STATUS_DESC"] == "Inactive":
                    barcodes[row["ITEM_ID"]]["inactive"] = row["ITEM_BARCODE"]
                else:
                    raise Exception(f"Weird {json.dumps(row)}")
            # print(json.dumps(barcodes, indent=4))
            # Do the stuff

            for idx, (item_id, bs) in enumerate(barcodes.items()):
                try:
                    inactive_barcode = bs["inactive"]
                    query = f'?query=(barcode="{inactive_barcode}")'
                    objects = list(
                        self.folio_client.folio_get_all(api_path, "items", query)
                    )
                    self.add_stats(f"{len(objects)} items found by barcode")
                    if len(objects) != 1:
                        logging.warning(
                            f"{len(objects)} Items found in folio for "
                            f"{item_id} {inactive_barcode}"
                        )
                        continue
                    current_item = objects[0]
                    current_item["barcode"] = bs["active"]
                    self.put_item(current_item, (item_id, bs))

                except Exception as ee:
                    logging.error(f"{ee} for {item_id} {json.dumps(bs)}")

                if idx % 10 == 0:
                    print(
                        f"{idx + 1} records processed. "
                        f"{json.dumps(self.stats, sort_keys=True)}"
                    )

    def put_item(self, item, row):
        try:
            item_path = "/item-storage/items"
            url = f'{self.folio_client.okapi_url}{item_path}/{item["id"]}'
            req = requests.put(
                url, data=json.dumps(item), headers=self.folio_client.okapi_headers
            )
            req.raise_for_status()
            self.add_stats("Successful updates")
            logging.debug(f"Successfully updated item from {json.dumps(row,indent=4)}")
        except Exception as ee:
            self.add_stats("Failed updates")
            logging.error(
                f"PUT failed: {url}\t{ee}\t" f'(Item UUID: {item["id"]}) {row}'
            )
            logging.error(f"Failed record\t{json.dumps(item)}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "input_file", "", "FileChooser")
        ServiceTaskBase.add_argument(parser, "results_folder", "", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "input_file", "")
        ServiceTaskBase.add_cli_argument(parser, "results_folder", "")
