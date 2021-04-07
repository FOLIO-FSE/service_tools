import csv
import json
import logging
import os
import time
import traceback
from abc import abstractmethod
from datetime import datetime as dt
from os.path import isfile

from folioclient import FolioClient

from helpers.custom_exceptions import TransformationProcessError, TransformationCriticalDataError
from service_tasks.service_task_base import ServiceTaskBase
from sierra_mapping.sierra_item_mapper import SierraItemTransformer


def setup_path(path, filename):
    path = os.path.join(path, filename)
    if not isfile(path):
        raise Exception(f"No file called {filename} present in {path}")
    return path


class SierraItemMigrator(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        csv.register_dialect("tsv", delimiter="\t")
        self.item_file = args.item_file
        self.instance_id_map = {}
        self.value_errors = 0
        self.map_path = args.map_path
        self.num_rows = 0
        self.locations = {}
        self.stats = {}
        self.results_path = args.result_path
        self.loan_type_map = {}
        self.material_type_map = {}
        self.locations_map = {}
        self.t0 = time.time()
        logging.info(f"Item file to process:{self.item_file}")
        logging.info(f"Saving results to {self.results_path}")
        self.migration_report_path = os.path.join(
            self.results_path, "iii_item_transformation_report.md"
        )

        try:
            # All the paths...
            instance_id_dict_path = setup_path(self.results_path, "instance_id_map.json")
            # items_map_path = setup_path(args.map_path, "item_mapping.json")
            # items_map_path = setup_path(args.map_path, "holdings_mapping.json")

            location_map_path = setup_path(self.map_path, "locations.tsv")
            loans_type_map_path = setup_path(self.map_path, "loan_types.tsv")
            call_number_type_map_path = setup_path(self.map_path, "call_number_type_mapping.tsv")
            material_type_map_path = setup_path(args.map_path, "material_types.tsv")
            self.folio_items_file_path = os.path.join(self.results_path, "folio_items.json")
            self.holdings_file_path = os.path.join(self.results_path, "folio_holdings.json")
            self.item_id_dict_path = os.path.join(self.results_path, "item_id_map.json")
            error_file_path = os.path.join(self.results_path, "item_transform_errors.tsv")

            # Material type mapping
            with open(material_type_map_path) as material_type_file:
                material_type_map = list(csv.DictReader(material_type_file, dialect="tsv"))
                logging.info(f"Found {len(material_type_map)} rows in material type map")
                logging.info(
                    f'{",".join(material_type_map[0].keys())} will be used for determining Material type'
                )

            # Loan type mapping
            with open(loans_type_map_path) as loans_type_file:
                loan_type_map = list(csv.DictReader(loans_type_file, dialect="tsv"))
                logging.info(f"Found {len(loan_type_map)} rows in loan type map")
                logging.info(
                    f'{",".join(loan_type_map[0].keys())} will be used for determining loan type'
                )

            # Call number type mapping
            with open(call_number_type_map_path) as call_number_type_map_file:
                call_number_type_map = list(
                    csv.DictReader(call_number_type_map_file, dialect="tsv")
                )
                logging.info(f"Found {len(call_number_type_map)} rows in callnumber type map")
                logging.info(
                    f'{",".join(call_number_type_map[0].keys())} '
                    "will be used for determining callnumber type"
                )

            # Instance id mapping
            with open(instance_id_dict_path, "r") as json_file:
                replaces = 0
                for index, json_string in enumerate(json_file):
                    # Format: {"legacy_id": "", "folio_id": "", "instanceLevelCallNumber": ""}
                    map_object = json.loads(json_string)
                    mapped_id = map_object["legacy_id"]
                    if mapped_id.startswith('.b'):
                        mapped_id = mapped_id[2:-1]
                        replaces += 1
                    elif mapped_id.startswith('b'):
                        mapped_id = mapped_id[1:]
                        replaces += 1
                    self.instance_id_map[mapped_id] = map_object
                    if index % 100000 == 0:
                        print(f"{index} instance ids loaded to map, {replaces} .b:s removed", end='\r')
                logging.info(f"loaded {index} migrated instance IDs")

            # Location mapping
            with open(location_map_path) as location_map_f:
                location_map = list(csv.DictReader(location_map_f, dialect="tsv"))
                logging.info(
                    f'{",".join(loan_type_map[0].keys())} will be used for determining location'
                )
                logging.info(f"Found {len(location_map)} rows in location map")

            self.transformer = SierraItemTransformer(folio_client, self.instance_id_map,
                                                     loan_type_map,
                                                     material_type_map,
                                                     location_map,
                                                     call_number_type_map)

        except TransformationProcessError as process_error:
            print("\n=======ERROR===========")
            print(f"{process_error}")
            print("\n=======Stack Trace===========")
            traceback.print_exc()

    def wrap_up(self):
        logging.info("Writing Holdings file to disk")
        self.print_holdings_file()
        logging.info("Done")
        logging.info("Writing Item Id map to disk")
        self.print_item_id_map()
        logging.info("Done")
        with open(self.migration_report_path, "w+") as report_file:
            self.migration_report = {**self.migration_report, **self.transformer.migration_report}
            self.stats = {**self.stats, **self.transformer.stats}
            self.print_dict_to_md_table(self.stats)
            report_file.write(f"# Sierra Item records transformation results   \n")
            report_file.write(f"Time Run: {dt.isoformat(dt.utcnow())}   \n")
            report_file.write(f"## Bibliographic records transformation counters   \n")
            self.write_migration_report(report_file)

    def print_holdings_file(self):
        logging.info("Writing holdings file.")
        if any(self.transformer.holdings):
            logging.info(f"Saving holdings created to {self.holdings_file_path}")
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
                except TransformationCriticalDataError as tcde:
                    logging.exception(tcde)
                except ValueError as value_error:
                    self.value_errors += 1
                    logging.exception(value_error)
                    if self.value_errors > 500:
                        raise Exception(f"More than 20 000 errors raised. Quitting.")
                if i % 10000 == 0:
                    logging.info(f"{i} rows processed. {self.value_errors} value errors")
            logging.info(f"Done. {i} rows processed")
            logging.info(" Wrapping up...")
            self.wrap_up()

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "item_file", "File of Sierra Items", "FileChooser")
        ServiceTaskBase.add_argument(parser, "result_path", "Results folder", "DirChooser")
        ServiceTaskBase.add_argument(parser, "map_path", "Mapping files folder", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "item_file", "File of Sierra Items")
        ServiceTaskBase.add_cli_argument(parser, "result_path", "Results folder")
        ServiceTaskBase.add_cli_argument(parser, "map_path", "Mapping files folder")
