import asyncio
import copy
import json
import logging
import sys
import time
from abc import abstractmethod
from os import listdir
from os.path import isfile, join

from pymarc import pymarc, Field, Leader

from service_tasks.service_task_base import ServiceTaskBase


# We are mimicing this behaviour:
# https://issues.folio.org/browse/MODOAIPMH-102

class Add952ToMarc(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.mat_type_map = {}
        for t in self.folio_client.folio_get_all("/material-types", "mtypes"):
            self.mat_type_map[t["id"]] = t["name"]
        logging.info(f"Loaded {len(self.mat_type_map)} material types")
        logging.info("Fetching locations")
        self.locations = list(self.folio_client.folio_get_all("/locations", "locations", ))
        logging.info(f"Fetched {len(self.locations)} locations")
        self.ref_data_dicts = {}
        self.file_paths = args.results_folder
        self.processed_records = 0
        files = [
            join(self.file_paths, f)
            for f in listdir(self.file_paths)
            if isfile(join(self.file_paths, f))]
        self.items_file = ""
        for file_name in files:
            if file_name.endswith("folio_holdings.json"):
                logging.info("Holdings file found")
                self.holdings_file = file_name
            elif file_name.endswith("folio_items.json"):
                logging.info("Items file found")
                self.items_file = file_name
            elif file_name.endswith("srs.json"):
                logging.info("Bibs file found")
                self.srs_file = file_name
        self.start = time.time()
        self.holdings_map = {}
        self.item_map = {}
        logging.info("Init done")

    def do_work(self):
        logging.info("Fetching Holdings records")
        self.start = time.time()
        with open(self.holdings_file) as holdings_file:
            idx = 0
            for row in holdings_file:
                hold = json.loads(row.split('\t')[-1])
                rec_map = {}
                idx += 1
                field_dict = {
                    "location": "",
                    "institution": "",
                    "campus": "",
                    "library": "",
                    "call_number": "",
                    "call_number_prefix": "",
                    "call_number_suffix": "",
                    "call_number_type": "",
                    "material_type": "",
                    "volume": "",
                    "enumeration": "",
                    "chronology": "",
                    "barcode": "",
                    "copy_number": "",
                    "instanceId": hold["instanceId"]
                }
                loc = self.get_ref_data_name(self.locations, "locations", hold["permanentLocationId"], "id")
                if loc:
                    field_dict["location"] = loc[1]
                else:
                    logging.info(f"location id {hold['permanentLocationId']} not found")

                if hold.get('callNumber', ""):
                    field_dict["call_number"] = hold['callNumber']

                if hold.get('callNumberPrefix', ""):
                    field_dict["call_number_prefix"] = hold['callNumberPrefix']

                if hold.get('callNumberSuffix', ""):
                    field_dict["call_number_suffix"] = hold['callNumberSuffix']

                if hold.get('callNumberTypeId', ""):
                    field_dict["call_number_type"] = hold['callNumberTypeId']

                if self.items_file:
                    self.holdings_map[hold["id"]] = field_dict
                else:
                    if hold["instanceId"] in self.item_map:
                        self.item_map[hold["instanceId"]].append(field_dict)
                    else:
                        self.item_map[hold["instanceId"]] = [field_dict]

                if idx % 200000 == 0:
                    elapsed = idx / (time.time() - self.start)
                    elapsed_formatted = f"{elapsed:,}"
                    logging.info(field_dict)
                    logging.info(
                        (f"{elapsed_formatted} recs/sec Number of records: {idx:,}."
                         f"Size of holdings map: {len(self.holdings_map)} holdings {sys.getsizeof(self.holdings_map) / (1024 * 1024 * 1024)}"))

        elapsed = idx / (time.time() - self.start)
        logging.info(f"Done parsing Holds in {(time.time() - self.start)} seconds")
        if self.items_file:
            logging.info("Fetching Items records")
            self.start = time.time()
            with open(self.items_file) as items_file:
                idx = 0
                for idx, row in enumerate(items_file):
                    item = json.loads(row.split('\t')[-1])
                    idx += 1
                    hold = self.holdings_map[item["holdingsRecordId"]]
                    item_field_dict = copy.deepcopy(hold)
                    if item.get("itemLevelCallNumber", ""):
                        item_field_dict["call_number"] = item["itemLevelCallNumber"]
                    if item.get("volume", ""):
                        item_field_dict["volume"] = item["volume"]
                    if item.get("materialTypeId", ""):
                        item_field_dict["material_type"] = item["materialTypeId"]
                    if item.get("enumeration", ""):
                        item_field_dict["enumeration"] = item["enumeration"]
                    if item.get("chronology", ""):
                        item_field_dict["chronology"] = item["chronology"]
                    if item.get("barcode", ""):
                        item_field_dict["barcode"] = item["barcode"]
                    if item.get("copyNumber", ""):
                        item_field_dict["copy_number"] = item["copyNumber"]

                    if hold["instanceId"] in self.item_map:
                        self.item_map[hold["instanceId"]].append(item_field_dict)
                    else:
                        self.item_map[hold["instanceId"]] = [item_field_dict]
                    if idx % 50000 == 0:
                        elapsed = idx / (time.time() - self.start)
                        elapsed_formatted = f"{elapsed:,}"
                        logging.info(json.dumps(item_field_dict, indent=4))
                        logging.info(
                            (f"{elapsed_formatted} recs/sec Number of records: {idx:,}."
                             f"Size of items map: {sys.getsizeof(self.holdings_map) / (1024 * 1024 * 1024)}")
                        )
            logging.info(f"Done parsing {idx} Items in {(time.time() - self.start)} seconds. {len(item_field_dict)}")

        self.start = time.time()
        with open(self.srs_file, "r", encoding="utf-8") as srs_file, open(join(self.file_paths, 'discovery_file.mrc'),
                                                                          'wb') as out:
            idx = 0
            found_locations = 0
            matched_instances = 0
            for row in srs_file:
                if len(row) < 100:
                    continue
                try:
                    idx += 1
                    srs_rec = json.loads(row.split("\t")[-1])
                    marc_record = from_json(srs_rec["parsedRecord"]["content"])
                    marc_record.remove_fields('952')
                    temp_leader = Leader(marc_record.leader)
                    temp_leader[9] = 'a'
                    marc_record.leader = temp_leader
                    instance_id = ""
                    for f999 in marc_record.get_fields('999'):
                        if 'i' in f999: 
                            instance_id = f999['i']
                    for item_data in self.item_map.get(instance_id, []):
                        found_locations += 1
                        my_field = Field(
                            tag="952",
                            indicators=["f", "f"],
                            subfields=[],
                        )
                        subfields = {
                            "d": item_data["location"],
                            "e": item_data["call_number"],
                            # "f", item_data[""],
                            # "g", item_data[""],
                            # "h", item_data[""],
                            "i": self.get_material_type_name(item_data["material_type"]),
                            # "j": item_data["volume"],
                            # "k": item_data["enumeration"],
                            # "l": item_data["chronology"],
                            # "m": item_data["barcode"],
                            # "n": item_data["copy_number"]
                        }
                        for sf_key, sf_value in subfields.items():
                            if sf_value:
                                my_field.add_subfield(sf_key, sf_value)
                        marc_record.add_ordered_field(my_field)
                    out.write(marc_record.as_marc())
                    if idx % 1000 == 0:
                        elapsed = idx / (time.time() - self.start)
                        elapsed_formatted = "{0:.2f}".format(elapsed)
                        logging.info(
                            (f"{elapsed_formatted} recs/sec Number of records: {idx:,}. "
                             f"Number of matched items: {found_locations} "
                             f'Example 952 field: {marc_record["952"]} {matched_instances}'),
                        )
                except Exception as ee:
                    logging.exception(f"row: {row}")
                    raise (ee)
            logging.info(
                f"Done parsing {idx} recs in {(time.time() - self.start)} seconds. Matched locs: {found_locations:,}")

    def process_record(self, marc_record):
        try:
            self.processed_records += 1
            if self.processed_records % 1000 == 0:
                elapsed = self.processed_records / (time.time() - self.start)
                elapsed_formatted = "{0:.2f}".format(elapsed)
                logging.info(
                    f"{elapsed_formatted} recs/sec Number of records: {self.processed_records:,}"
                )
        except Exception as ee:
            logging.exception(ee)

    def get_ref_data_name(self, ref_data, ref_name, key_value, key_type):
        dict_key = f"{ref_name}{key_value}"
        if dict_key not in self.ref_data_dicts:
            d = {}
            for r in ref_data:
                d[r[key_type].lower()] = (r["id"], r["discoveryDisplayName"])
            self.ref_data_dicts[dict_key] = d
        ref_object = (
            self.ref_data_dicts[dict_key][key_value.lower()]
            if key_value.lower() in self.ref_data_dicts[dict_key]
            else None
        )
        if not ref_object:
            logging.debug(f"No matching element for {key_value} in {list(ref_data)}")
            return None
        return ref_object

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "results_folder", "Path to the results folder", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "results_folder", "Path to the results folder")

    def get_material_type_name(self, material_type_uuid):
        try:
            return self.mat_type_map[material_type_uuid]
        except KeyError:
            logging.error(f"Material type '{material_type_uuid}' not found")
            return ""


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


@background
def parse_stuff(marc_record):
    if '245' in marc_record:
        f = marc_record['245'].format_field()
    if '100' in marc_record:
        for f in marc_record.get_fields('100'):
            ff = f.format_field()


def from_json(json_object):
    rec = pymarc.Record()
    rec.leader = json_object["leader"]
    for field in json_object["fields"]:
        k, v = list(field.items())[0]
        if "subfields" in v and hasattr(v, "update"):
            # flatten m-i-j dict to list in pymarc
            subfields = []
            for sub in v["subfields"]:
                for code, value in sub.items():
                    subfields.extend((code, value))
            fld = pymarc.Field(
                tag=k, subfields=subfields, indicators=[v["ind1"], v["ind2"]]
            )
        else:
            fld = pymarc.Field(tag=k, data=v)
        rec.add_ordered_field(fld)
    return rec
