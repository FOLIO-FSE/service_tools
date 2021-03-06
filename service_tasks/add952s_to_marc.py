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

        self.institutions = list(self.folio_client.get_all("/location-units/institutions", "locinsts", ))
        logging.info(f"Fetched {len(self.institutions)} institutions")

        self.campuses = list(self.folio_client.get_all("/location-units/campuses", "loccamps", ))
        logging.info(f"Fetched {len(self.campuses)} campuses")

        self.libraries = list(self.folio_client.get_all("/location-units/libraries", "loclibs", ))
        logging.info(f"Fetched {len(self.libraries)} libraries")

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
            for idx, row in enumerate(holdings_file):
                try:
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
                        "instanceId": hold["instanceId"],
                        "matched_item": False
                    }
                    loc_structure = self.get_location_structure(self.locations, "locations", hold["permanentLocationId"], "id")
                    # loc = self.get_ref_data_name(self.locations, "locations", hold["permanentLocationId"], "id")
                    if loc_structure:
                        field_dict["institution"] = loc_structure[1]
                        field_dict["campus"] = loc_structure[2]
                        field_dict["library"] = loc_structure[3]
                        field_dict["location"] = loc_structure[4]
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
                        # If there is an Items file, we add these to the holdings map
                        self.holdings_map[hold["id"]] = field_dict
                    else:
                        # No items file, add these directly as "Items" that will generate 952:s
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
                except Exception as ee:
                    logging.error(f"{ee} - {row}")

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
                    hold = self.holdings_map.get(item["holdingsRecordId"], {})
                    if not hold:
                        logging.error(f'{item["holdingsRecordId"]} was not found in list of holdings')
                    else:
                        hold['matched_item'] = True
                        item_field_dict = copy.deepcopy(hold)
                        if item.get("itemLevelCallNumber", ""):
                            item_field_dict["call_number"] = item["itemLevelCallNumber"]
                        if item.get("itemLevelCallNumberPrefix", ""):
                            item_field_dict["call_number_prefix"] = item["itemLevelCallNumberPrefix"]
                        if item.get("itemLevelCallNumberSuffix", ""):
                            item_field_dict["call_number_suffix"] = item["itemLevelCallNumberSuffix"]
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
                            logging.info(
                                (f"{elapsed_formatted} recs/sec Number of records: {idx:,}."
                                 f"Size of items map: {sys.getsizeof(self.item_map) / (1024 * 1024 * 1024)}")
                            )
            logging.info(f"Done parsing {idx} Items in {(time.time() - self.start)} seconds. {len(self.item_map)}")
            logging.info("moving item-less holdings to item_map")
            holdings_without_items = {value['instanceId']: [value] for (key, value) in self.holdings_map.items() if
                                      not value['matched_item']}
            # logging.info(list(holdings_without_items.items())[0])
            logging.info(
                f"Done parsing {(len(holdings_without_items))} Item-less holdings in {(time.time() - self.start)} seconds. {len(self.item_map)}")

        self.start = time.time()
        with open(self.srs_file, "r", encoding="utf-8") as srs_file, open(join(self.file_paths, 'discovery_file.mrc'),
                                                                          'wb') as out:
            idx = 0
            found_locations = 0
            matched_holdings = 0
            matched_instances = 0
            for row in srs_file:
                if len(row) < 100:
                    continue
                try:
                    idx += 1

                    srs_rec = json.loads(row.split("\t")[-1])
                    marc_record = from_json(srs_rec["parsedRecord"]["content"])
                    marc_record.remove_fields('952', '945', '907', '998')
                    temp_leader = Leader(marc_record.leader)
                    temp_leader[9] = 'a'
                    marc_record.leader = temp_leader
                    instance_id = ""
                    for f999 in marc_record.get_fields('999'):
                        if 'i' in f999:
                            instance_id = f999['i']
                    num_952s = 0
                    for holdings_data in holdings_without_items.get(instance_id, []):
                        found_locations += 1
                        matched_holdings += 1
                        my_field = self.create_952_from_item_data(holdings_data)
                        if num_952s < 50:
                            marc_record.add_ordered_field(my_field)
                        num_952s += 1

                    for item_data in self.item_map.get(instance_id, []):
                        found_locations += 1
                        my_field = self.create_952_from_item_data(item_data)
                        if num_952s < 50:
                            marc_record.add_ordered_field(my_field)
                        num_952s += 1
                    out.write(marc_record.as_marc())
                    if idx % 2000 == 0:
                        elapsed = idx / (time.time() - self.start)
                        elapsed_formatted = "{0:.2f}".format(elapsed)
                        logging.info(
                            (f"{elapsed_formatted} recs/sec Number of records: {idx:,}. "
                             f"Number of matched items: {found_locations} Matched holdings: {matched_holdings} "
                             f'Example 952 field: {marc_record["952"]} {matched_instances}'),
                        )
                except Exception as ee:
                    logging.exception(f"row: {row}")
                    raise (ee)
            logging.info(
                f"Done parsing {idx} recs in {(time.time() - self.start)} seconds. Matched locs: {found_locations:,}")

    def create_952_from_item_data(self, item_data):
        my_field = Field(
            tag="952",
            indicators=["f", "f"],
            subfields=[],
        )
        subfields = {
            "a": item_data["institution"],
            "b": item_data["campus"],
            "c": item_data["library"],
            "d": item_data["location"],
            "e": item_data["call_number"],
            "f": item_data["call_number_prefix"],
            "g": item_data["call_number_prefix"],
            # "h", item_data[""],
            "i": self.get_material_type_name(item_data["material_type"]),
            "j": item_data["volume"],
            "k": item_data["enumeration"],
            "l": item_data["chronology"],
            "m": item_data["barcode"],
            "n": item_data["copy_number"]
        }
        for sf_key, sf_value in subfields.items():
            if sf_value:
                my_field.add_subfield(sf_key, sf_value)
        return my_field

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
                d[r[key_type].lower()] = (r["id"], r["name"])
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

    # self.get_ref_data_name(self.locations, "locations", hold["permanentLocationId"], "id")
    def get_location_structure(self, ref_data, ref_name, key_value, key_type):
        dict_key = f"{ref_name}{key_value}"
        if dict_key not in self.ref_data_dicts:
            d = {}
            for r in ref_data:
                institution = self.get_ref_data_name(self.institutions, "institutions", r["institutionId"], "id")[1]
                campus = self.get_ref_data_name(self.campuses, "campuses", r["campusId"], "id")[1]
                library = self.get_ref_data_name(self.libraries, "libraries", r["libraryId"], "id")[1]
                d[r[key_type].lower()] = (r["id"], institution, campus, library,  r["name"])
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
            # logging.error(f"Material type '{material_type_uuid}' not found")
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
