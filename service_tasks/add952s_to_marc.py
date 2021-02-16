import json
import logging
import multiprocessing
import sys
import time
import traceback
from abc import abstractmethod

from os import listdir
from os.path import isfile, join

from pymarc import MARCReader, pymarc, Field, Record, XMLWriter

from service_tasks.service_task_base import ServiceTaskBase
import asyncio


class Add952ToMarc(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("Fetching locations")
        self.locations = list(self.folio_client.folio_get_all("/locations", "locations", ))
        print(f"Fetched {len(self.locations)} locations")
        self.ref_data_dicts = {}
        self.file_paths = args.marc_files
        self.processed_records = 0
        files = [
            join(self.file_paths, f)
            for f in listdir(self.file_paths)
            if isfile(join(self.file_paths, f))]
        for file_name in files:
            if file_name.endswith("folio_holdings.json"):
                print("Holdings file found")
                self.holdings_file = file_name
            elif file_name.endswith("srs.json"):
                print("Bibs file found")
                self.srs_file = file_name
            else:
                raise Exception(f"unexpected file in {self.file_paths}")
        self.start = time.time()
        self.holdings_map = {}
        print("Init done")

    def do_work(self):
        print("Fetching Holdings records")
        self.start = time.time()
        with open(self.holdings_file) as holdings_file:
            idx = 0
            for row in holdings_file:
                hold = json.loads(row)
                idx += 1

                loc = self.get_ref_data_name(self.locations, "locations", hold["permanentLocationId"], "id")
                if loc:
                    if hold["instanceId"] in self.holdings_map:
                        self.holdings_map[hold["instanceId"]].append(loc[1])
                    else:
                        self.holdings_map[hold["instanceId"]] = [loc[1]]
                else:
                    print(f"location id {hold['permanentLocationId']} not found")
                if idx % 200000 == 0:
                    elapsed = idx / (time.time() - self.start)
                    elapsed_formatted = f"{elapsed:,}"
                    print(
                        (f"{elapsed_formatted} recs/sec Number of records: {idx:,}."
                         f"Size of holdings map: {sys.getsizeof(self.holdings_map)/(1024*1024*1024)}"),
                        flush=True,
                    )
        elapsed = idx / (time.time() - self.start)
        print(f"Done parsing Holds in {(time.time() - self.start)} seconds")
        self.start = time.time()
        writer = XMLWriter(open(join(self.file_paths, 'file.xml'), 'wb'))

        with open(self.srs_file) as srs_file:
            idx = 0
            found_locations = 0
            for row in srs_file:

                if len(row) < 100:
                    continue
                try:
                    idx += 1
                    srs_rec = json.loads(row.split("\t")[-1])
                    marc_record = from_json(srs_rec["parsedRecord"]["content"])
                    for loc in self.holdings_map.get(marc_record['999']["i"], []):
                        found_locations += 1
                        marc_record.add_ordered_field(
                            Field(
                                tag="952",
                                indicators=["f", "f"],
                                subfields=["d", loc],
                            ))
                        writer.write(marc_record)
                    if idx % 1000 == 0:
                        print(marc_record["952"])
                        elapsed = idx / (time.time() - self.start)
                        elapsed_formatted = "{0:.2f}".format(elapsed)
                        print(
                            (f"{elapsed_formatted} recs/sec Number of records: {idx:,}. "
                             f"Number of matched holdings: {found_locations:,}"),
                            flush=True,
                        )
                except Exception as ee:
                    print(f"row: {row}")
                    writer.close()
                    raise(ee)
            writer.close()  # Important!
            print(f"Done parsing {idx} recs in {(time.time() - self.start)} seconds. Matched locs: {found_locations:,}")

    def process_record(self, marc_record):
        try:
            self.processed_records += 1
            if self.processed_records % 1000 == 0:
                elapsed = self.processed_records / (time.time() - self.start)
                elapsed_formatted = "{0:.2f}".format(elapsed)
                print(
                    f"{elapsed_formatted} recs/sec Number of records: {self.processed_records:,}",
                    flush=True,
                )
        except Exception as ee:
            print(ee)

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
        ServiceTaskBase.add_argument(parser, "marc_files", "Path to the file", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "marc_files", "Path to the file")


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