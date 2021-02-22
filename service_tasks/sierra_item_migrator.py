import csv
import json
import os
import time
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase
from sierra_mapping.sierra_item_mapper import SierraItemTransformer
from datetime import datetime as dt

class SierraItemMigrator(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        csv.register_dialect("tsv", delimiter="\t")
        self.item_file = args.item_file
        self.instance_id_map = {}
        self.value_errors = 0
        self.mappings_files_folder = args.mappings_files_folder
        self.num_rows = 0
        self.locations = {}
        self.stats = {}

        self.loan_type_map = {}
        self.material_type_map = {}
        self.locations_map = {}
        self.t0 = time.time()

        print("\tFiles from {}".format(self.item_file))
        print("\tSaving results to {}".format(args.results_folder))

        self.migration_report_path = os.path.join(
            args.results_folder, "instance_transformation_report.md"
        )

        # set up loan type mapping
        self.loan_types = list(self.folio_client.folio_get_all("/loan-types", "loantypes"))
        print(f"Fetched {len(self.loan_types)} loan types from server")
        with open(os.path.join(args.mappings_files_folder, "loan_types.tsv")) as loan_type_file:
            for t in csv.DictReader(loan_type_file, dialect="tsv"):
                match = next(f for f in self.loan_types if f["name"].lower() == t['folio_name'].lower())
                self.loan_type_map[t["legacy_code"]] = match["id"]
        print(f"Loaded {len(self.loan_type_map)} loan type mappings")

        # setup material type mapping
        self.material_types = list(self.folio_client.folio_get_all("/material-types", "mtypes"))
        print(f"Fetched {len(self.material_types)} material types from server")
        with open(os.path.join(args.mappings_files_folder, "material_types.tsv")) as material_type_file:
            for t in csv.DictReader(material_type_file, dialect="tsv"):
                match = next(f for f in self.material_types if f["name"].lower() == t['folio_name'].lower())
                self.material_type_map[t["legacy_code"]] = match["id"]
        print(f"Loaded {len(self.material_type_map)} material_types mappings")

        # setup locations
        print("Fetching locations...")
        self.locations = list(self.folio_client.folio_get_all("/locations", "locations"))
        print(f"Fetched {len(self.locations)} locations from server")
        default_loc_id = next(f['id'] for f in self.locations if f["code"] == "tech")
        with open(os.path.join(args.mappings_files_folder, "locations.tsv")) as loc_file:
            for t in csv.DictReader(loc_file, dialect="tsv"):
                try:
                    match = next(f for f in self.locations if f["code"].lower() == t['folio_code'].lower())
                    self.locations_map[t["legacy_code"]] = match["id"]
                except StopIteration:
                    self.add_to_migration_report("Legacy location codes not properly mapped", t["legacy_code"])
                    self.locations_map[t["legacy_code"]] = default_loc_id
            self.locations_map['*'] = default_loc_id
        print(f"Loaded {len(self.locations_map)} location mappings")

        with open(args.instance_id_dict_path, "r") as json_file:
            for index, json_string in enumerate(json_file):
                # {"legacy_id": legacy_id, "folio_id": folio_instance["id"], "instanceLevelCallNumber": instance_level_call_number}
                map_object = json.loads(json_string)
                self.instance_id_map[map_object["legacy_id"].replace(".", "")] = map_object
        print(f"loaded {index} migrated instance IDs")

        self.folio_items_file_path = os.path.join(args.results_folder, "folio_items.json")
        self.holdings_file_path = os.path.join(args.results_folder, "folio_holdings.json")
        self.item_id_dict_path = os.path.join(args.results_folder, "item_id_map.json")

        self.transformer = SierraItemTransformer(folio_client, self.instance_id_map, self.loan_type_map,
                                                 self.material_type_map, self.locations_map)

    def wrap_up(self):
        print("Writing Holdings file to disk")
        self.print_holdings_file()
        print("Done")
        print("Writing Item Id map to disk")
        self.print_item_id_map()
        print("Done")
        with open(self.migration_report_path, "w+") as report_file:
            self.migration_report = {**self.migration_report, **self.transformer.migration_report}
            self.stats = {**self.stats, **self.transformer.stats}
            self.print_dict_to_md_table(self.stats)
            report_file.write(f"# Sierra Item records transformation results   \n")
            report_file.write(f"Time Run: {dt.isoformat(dt.utcnow())}   \n")
            report_file.write(f"## Bibliographic records transformation counters   \n")
            self.write_migration_report(report_file)

    def print_holdings_file(self):
        print("Writing holdings file.")
        if any(self.transformer.holdings):
            print(f"Saving holdings created to {self.holdings_file_path}")
            with open(self.holdings_file_path, "w+") as holdings_file:
                for key, holding in self.transformer.holdings.items():
                    self.transformer.write_object(holding, holdings_file)
                    self.add_stats("Holdings Records Written to disk")

    def print_item_id_map(self):
        with open(self.item_id_dict_path, "w+") as json_file:
            json.dump(self.transformer.item_id_map, json_file, indent=4)
        self.stats["Map of Sierra to Item IDs Written to disk"] = len(
            self.item_id_dict_path
        )

    def count_statuses(self, sierra_item):
        status = sierra_item.get("status", {}).get("display", "")
        due_date = sierra_item.get("status", {}).get("duedate")
        self.add_to_migration_report("Sierra Item Statuses", f"{status} Due date: {bool(due_date)}")

    def do_work(self):
        start = time.time()
        with open(self.folio_items_file_path, "w+") as items_file, open(self.item_file, "r") as from_file:
            line = ""
            i = 0
            for line in from_file:
                i += 1
                try:
                    sierra_item = json.loads(line)
                    if i == 1:
                        print(json.dumps(sierra_item, indent=4))
                    if sierra_item["deleted"] is not True and len(sierra_item["bibIds"]) > 0:
                        self.transformer.transform(sierra_item, items_file)
                except ValueError as value_error:
                    self.value_errors += 1
                    print(value_error)
                    if self.value_errors > 1000:
                        raise value_error
                if i % 1000 == 0:
                    print(f"{i} rows processed. {self.value_errors} valueerrors")
            print(f"Done. {i} rows processed")
            print(" Wrapping up...")
            self.wrap_up()

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "item_file", "File of Sierra Items", "FileChooser")
        ServiceTaskBase.add_argument(parser, "instance_id_dict_path", "", "FileChooser")
        ServiceTaskBase.add_argument(parser, "results_folder", "Results folder", "DirChooser")

        ServiceTaskBase.add_argument(parser, "mappings_files_folder", "Mapping files folder", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "item_file", "File of Sierra Items")
        ServiceTaskBase.add_cli_argument(parser, "instance_id_dict_path", "")
        ServiceTaskBase.add_cli_argument(parser, "results_folder", "Results folder")
        ServiceTaskBase.add_cli_argument(parser, "mappings_files_folder", "Mapping files folder")
