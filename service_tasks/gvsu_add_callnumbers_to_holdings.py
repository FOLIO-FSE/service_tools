import csv
import json
import logging
import time
from abc import abstractmethod
from pathlib import Path

import requests

from helpers.custom_dict import InsensitiveDictReader
from service_tasks.service_task_base import ServiceTaskBase


class GVSUAddCallnumbersToHoldings(ServiceTaskBase):
    def __init__(self, folio_client, args):
        csv.register_dialect("tsv", delimiter="\t")
        super().__init__(folio_client, "", args.results_folder)
        self.instance_ids = []
        self.args = args

    def do_work(self):
        time_stamp = time.strftime("%Y%m%d-%H%M%S")
        failed_path = Path(self.args.results_folder) / f'failed_recs_{time_stamp}.tsv'
        with open(failed_path, "w+", newline='') as failed_file:
            failed_writer = None
            api_path = "/inventory/instances"
            hold_path = "/holdings-storage/holdings"
            with open(self.args.input_file, 'r', encoding="utf-8") as input_file:
                for idx, row in enumerate(csv.DictReader(input_file, dialect="tsv")):
                    try:
                        if idx == 0:
                            print(list(row.keys()))
                            print(row)
                            failed_writer = csv.DictWriter(failed_file, dialect='tsv', fieldnames=list(row.keys()))
                            failed_writer.writeheader()
                            failed_file.flush()
                        bib_id = row["Record Number(Bibliographic)"]
                        if row.get("090", "") or row.get("050", "") or row.get("086", ""):
                            query = f'?limit=100&query=(identifiers =/@value \"{bib_id}\")'
                            objects = list(self.folio_client.folio_get_all(api_path, "instances", query))
                            if len(objects) != 1:
                                logging.warning(f"{len(objects)} Instances found in folio for {bib_id}. Skipping")
                            else:
                                instance_id = objects[0].get("id")
                                hold_query = f"?limit=1000&query=instanceId=={instance_id}"
                                holdings = list(
                                    self.folio_client.folio_get_all(hold_path, "holdingsRecords", hold_query))
                                if not holdings:
                                    logging.warning(
                                        f"{len(holdings)} holdings found for Instance {instance_id} "
                                        f"(Bib id: {bib_id}). Skipping")
                                else:
                                    for holding in holdings:
                                        self.update_and_put_holdings(bib_id, hold_path, holding, instance_id, row,
                                                                     failed_writer)
                        else:
                            self.add_stats("Rows in file w/o any callNumbers")
                    except Exception as ee:
                        failed_writer.writerow(row)
                        logging.error(f"{ee}")

                    if idx % 10 == 0:
                        print(f'{idx + 1} records processed. {json.dumps(self.stats, sort_keys=True)}')

    def update_and_put_holdings(self, bib_id, hold_path, holding, instance_id, row, failed_writer):
        try:
            prev_call_number = holding.get("callNumber", "")
            lc_callnumber_type = "95467209-6d7b-468b-94df-0f5d7ad2747d"
            if row.get("086", ""):
                self.add_stats("086:s added")
                holding["callNumber"] = row.get("086")
                sudoc_call_number_type = "fc388041-6cd0-4806-8a74-ebe3b9ab4c6e"
                holding["callNumberTypeId"] = sudoc_call_number_type
            elif row.get("090", ""):
                self.add_stats("090:s added")
                holding["callNumber"] = row.get("090")
                holding["callNumberTypeId"] = lc_callnumber_type
            elif row.get("050", ""):
                self.add_stats("050:s added")
                holding["callNumber"] = row.get("050")
                holding["callNumberTypeId"] = lc_callnumber_type
            url = f'{self.folio_client.okapi_url}{hold_path}/{holding["id"]}'
            req = requests.put(url, data=json.dumps(holding),
                               headers=self.folio_client.okapi_headers)
            req.raise_for_status()
            self.add_stats("Successful updates")
            logging.debug(
                f'Successfully changed callNumber from "{prev_call_number}" to '
                f'{holding["callNumber"]} for {instance_id} (Holdings UUID: {holding["id"]})')
        except Exception as ee:
            self.add_stats("Failed updates")
            failed_writer.writerow(row)
            logging.error(
                f'PUT failed: {url}\t{ee} for {instance_id} (Bib id: {bib_id}) '
                f'(Holdings UUID: {holding["id"]})')
            logging.error(f"Failed record\t{json.dumps(holding)}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "input_file", "",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser, "results_folder", "",
                                     "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "input_file", "")
        ServiceTaskBase.add_cli_argument(parser, "results_folder", "")
