import json

from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import sys, csv
import pandas as pd


class CornellReplaceMfhdIdsWithUuids(ServiceTaskBase):
    def __init__(self, args):
        self.item_file_path = args.item_file_path
        self.holdings_id_file_path = args.holdings_id_file_path
        self.results_file_path = args.results_file_path
        self.instance_id_map = {}

    def do_work(self):
        with open(self.holdings_id_file_path, "r") as holdings_id_file:
                # {"legacy_id": legacy_id, "folio_id": folio_instance["id"], "instanceLevelCallNumber": instance_level_call_number}
                self.instance_id_map = json.load(holdings_id_file)
                print(len(self.instance_id_map))
        with open(self.item_file_path, "r") as item_file, open(self.results_file_path, "w") as results_file:
            missing = 0
            for index, json_item in enumerate(item_file):
                item = json.loads(json_item)
                try:
                    item['holdingsRecordId'] = self.instance_id_map[item['holdingsRecordId']]["id"]
                    results_file.write(f"{json.dumps(item)}\n")
                except Exception:
                    missing += 1
        print(missing)
        print("Done!", flush=True)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "item_file_path", "Delimited file containing field to analyze",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser, "holdings_id_file_path", "Delimited file containing field to analyze",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser, "results_file_path", "Delimited file containing field to analyze",
                                     "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "item_file_path", "Delimited file containing field to analyze")
        ServiceTaskBase.add_cli_argument(parser, "holdings_id_file_path", "Delimited file containing field to analyze")
        ServiceTaskBase.add_cli_argument(parser, "results_file_path", "Delimited file containing field to analyze")
