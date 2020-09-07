import csv
import json
import os
import sys
import uuid
from abc import abstractmethod
from concurrent.futures.process import ProcessPoolExecutor
from io import StringIO

import pymarc
from pymarc import Field, JSONWriter, XMLWriter

from service_tasks.service_task_base import ServiceTaskBase


class AddHRIDToMARCRecords(ServiceTaskBase):
    def __init__(self, folio_client, source_path: str, result_path: str, id_map_path: str):
        super().__init__(folio_client)
        self.result_path = result_path
        self.source_path = source_path
        self.id_map = {}
        self.srs_records_file = open(os.path.join(self.result_path, "srs.json"), "w+")
        self.srs_marc_records_file = open(os.path.join(self.result_path, "srs_marc_records.json"), "w+")
        self.srs_raw_records_file = open(os.path.join(self.result_path, "srs_raw_records.json"), "w+")
        self.marc_xml_writer = XMLWriter(
            open(os.path.join(self.result_path, "marc_xml_dump.xml"), "wb+")
        )
        self.recs_to_save = []
        with open(id_map_path) as id_map_file:
            self.id_map = list(csv.DictReader(id_map_file))
        self.expected_rows = len(self.id_map)
        print(f"Number of rows in map: {self.expected_rows}")

    def do_work(self):
        i = 0
        with open(os.path.join(self.source_path, "srs_marc_records.json")) as srs_marc_file:
            for row in srs_marc_file:
                i += 1
                split_row = row.split('\t')
                obj = json.loads(split_row[1])
                marc_record = from_json(obj["content"])
                if "003" in marc_record:
                    __003 = marc_record['003']
                    marc_record.remove_field(__003)
                instance_id = marc_record["999"]["i"]
                hrid = next((h["hrid"] for h in self.id_map if instance_id == h["uuid"]), "")
                srs_id = marc_record["999"]["s"]
                prefixes1 = ["MSSC", "()", "Ex Libris Bib ID"]
                if "001" in marc_record and marc_record["001"] and marc_record["001"].data:
                    old_001 = marc_record["001"].data
                    prefixes = ["(ocn)", "ocn", "(ocm)", "ocm"]
                    for p in prefixes:
                        if old_001.strip().startswith(p):
                            self.add_stats(f"prefix {p} found in 001")
                            old_001.replace(p, "(OCoLC)")
                    if "(OCoLC)" not in old_001 and not old_001[0].isalpha():
                        old_001 = f"(OCoLC){old_001}"
                    marc_record.add_ordered_field(Field(tag="035", indicators=[' ', ' '], subfields=['a', old_001]))
                    for f in marc_record.get_fields("035"):
                        if "a" in f and f["a"]:
                            for p in prefixes1:
                                if p in f["a"]:
                                    self.add_stats(f"Prefix in 035 {p}")
                                    marc_record.remove_field(f)
                    if hrid:
                        marc_record["001"].data = hrid
                        self.recs_to_save.append((marc_record, instance_id, srs_id,
                                                  self.folio_client.get_metadata_construct()))
                        self.marc_xml_writer.write(marc_record)
                    if i % 1000 == 0:
                        # print(f"{i}\t{self.stats}", end="\r")
                        print("progress: {}/{}".format(i + 1, self.expected_rows))
                        sys.stdout.flush()
                    if len(self.recs_to_save) == 1000:
                        self.flush_srs_recs()
                        self.recs_to_save = []
            self.flush_srs_recs()
            self.marc_xml_writer.close()
            self.srs_raw_records_file.close()
            self.srs_records_file.close()
            self.srs_marc_records_file.close()
            self.print_dict_to_md_table(self.stats)

    def flush_srs_recs(self):
        pool = ProcessPoolExecutor(max_workers=4)
        results = list(pool.map(get_srs_strings, self.recs_to_save))
        self.srs_records_file.write("".join(r[0] for r in results))
        self.srs_marc_records_file.write("".join(r[2] for r in results))
        self.srs_raw_records_file.write("".join(r[1] for r in results))

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        parser.add_argument("source_path", widget="DirChooser")
        parser.add_argument("results_path", widget="DirChooser")
        parser.add_argument("id_map_path", widget="FileChooser")


def from_json(jobj):
    rec = pymarc.Record()
    rec.leader = jobj["leader"]
    for field in jobj["fields"]:
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


def get_srs_strings(my_tuple):
    marc_record = my_tuple[0]
    instance_id = my_tuple[1]
    srs_id = my_tuple[2]
    metadata_construct = my_tuple[3]
    json_string = StringIO()
    writer = JSONWriter(json_string)
    writer.write(marc_record)
    writer.close(close_fh=False)
    marc_uuid = str(uuid.uuid4())
    raw_uuid = str(uuid.uuid4())
    record = {
        "id": srs_id,
        "deleted": False,
        "snapshotId": "67dfac11-1caf-4470-9ad1-d533f6360bdd",
        "matchedProfileId": str(uuid.uuid4()),
        "matchedId": str(uuid.uuid4()),
        "generation": 1,
        "recordType": "MARC",
        "rawRecordId": raw_uuid,
        "parsedRecordId": marc_uuid,
        "additionalInfo": {"suppressDiscovery": False},
        "externalIdsHolder": {"instanceId": instance_id},
        "metadata": metadata_construct,
    }
    raw_record = {"id": raw_uuid, "content": marc_record.as_json()}
    marc_record = {"id": marc_uuid, "content": json.loads(marc_record.as_json())}
    return (
        f"{record['id']}\t{json.dumps(record)}\n",
        f"{raw_record['id']}\t{json.dumps(raw_record)}\n",
        f"{marc_record['id']}\t{json.dumps(marc_record)}\n",
    )
