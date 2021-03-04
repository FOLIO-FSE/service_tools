import calendar
import csv
import json
import os
import re
import time
import traceback
import uuid
from abc import abstractmethod
from datetime import datetime

from folioclient import FolioClient
from pymarc import MARCReader

from service_tasks.service_task_base import ServiceTaskBase


class TransformMarcCRecords(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        csv.register_dialect("tsv", delimiter="\t")
        self.records_file = args.records_file
        self.result_path = args.result_path
        self.instance_id_map = {}
        print(f"reading locations map from {args.location_map_path}")
        with open(args.location_map_path) as locations_map_file:
            self.locations_map = list(csv.DictReader(locations_map_file, dialect="tsv"))

        with open(args.instance_id_map_path) as id_map_file:
            for index, json_string in enumerate(id_map_file):
                # Format is {"legacy_id", "folio_id","instanceLevelCallNumber"}\n
                if index % 100000 == 0:
                    print(f"{index} instance ids loaded to map", end='\r')
                map_object = json.loads(json_string)
                self.instance_id_map[map_object["legacy_id"]] = map_object
            print(f"loaded {index} migrated instance IDs")

        self.results = {}
        self.holdings_schema = folio_client.get_holdings_schema()
        self.stats = {}
        self.mapped_folio_holdings_fields = {}
        self.unmapped_holdings_fields = {}
        self.migration_report = {}
        self.num_recs = 0
        self.failed_records = []
        self.hlm_export = []
        self.duplicate_holdings = {}
        self.created_holdings = {}
        self.t0 = time.time()
        self.longest_statement = ""
        self.instances = {}
        self.longest_statement_len = 0
        print("Init done.")

    def do_work(self):
        with open(self.records_file, "rb") as marc_file:
            reader = MARCReader(marc_file, "rb", permissive=True)
            reader.hide_utf8_warnings = True
            for record in reader:
                self.add_stats("Total number of C-records in file")
                if record is None:
                    self.add_to_migration_report(
                        "MARC reader exception",
                        f"Current chunk: {reader.current_chunk} was ignored because the following exception: "
                        f"{reader.current_exception}",
                    )
                    self.failed_records.append(reader.current_chunk)
                else:
                    try:
                        location = self.get_location(record)
                        instance_id = self.get_instance_id(record)
                        if not instance_id:
                            self.add_stats("C-records without migrated instances")
                            self.add_to_migration_report(
                                "No Instance found",
                                f"No instance id found for {record['001'].format_field()}"
                                f"004: {record['004'].format_field()}",
                            )
                        else:
                            if location:
                                stmt = list(self.get_holdings_statements(record, "853", "863", "866"))
                                stmt_suppl = list(
                                    (s[0] for s in self.get_holdings_statements(record, "854", "864", "867") if s[0])
                                )
                                stmt_index = list(
                                    (s[0] for s in self.get_holdings_statements(record, "855", "865", "868") if s[0])
                                )
                                h_stmt = list((s[0] for s in stmt if s[0]))
                                hsss = sorted(set(s[1] for s in stmt if s[1]))
                                holdings_record = {
                                    "instanceId": instance_id,
                                    "formerIds": [record["001"].format_field()],
                                    "permanentLocationId": location,
                                    "id": str(uuid.uuid4()),
                                    "callNumber": get_call_number(record),
                                    "notes": list(get_notes(record)),
                                    "holdingsStatements": h_stmt,
                                    "metadata": self.folio_client.get_metadata_construct(),
                                }
                                if stmt_index:
                                    holdings_record[
                                        "holdingsStatementsForIndexes"
                                    ] = stmt_index
                                if stmt_suppl:
                                    holdings_record[
                                        "holdingsStatementsForSupplements"
                                    ] = stmt_suppl
                                hlm_row = self.parse_hlm(hsss, holdings_record)
                                if hlm_row:
                                    self.hlm_export.append(hlm_row)

                                key = to_key(holdings_record)
                                if key in self.created_holdings:
                                    self.add_stats("Duplicate holdings")
                                    self.add_to_migration_report(
                                        "Duplicate C-records that were merged",
                                        f"probable duplicate c-record. "
                                        f"001: {record['001'].format_field()} "
                                        f"004: {record['004'].format_field()}",
                                    )
                                    self.merge_holding(holdings_record)
                                else:
                                    self.created_holdings[key] = holdings_record
                                    hsss = sorted(set(s[1] for s in stmt if s[1]))

                            else:
                                self.add_stats("No location, skipped")
                    except Exception as exception:
                        print(exception)
                        traceback.print_exc()
                        print(record)

    def wrap_up(self):
        # Wrap up
        if any(self.hlm_export):
            write_hlm_export(self.hlm_export, self.result_path)

        if any(self.created_holdings):
            holdings_path = os.path.join(self.result_path, "folio_c_record_holdings.json")
            print(f"Saving holdings created from c-records to {holdings_path}")
            with open(holdings_path, "w+") as holdings_file:
                for key, holding in self.created_holdings.items():
                    self.validate(holding)
                    self.count_unmapped_fields(holding)
                    write_to_file(holdings_file, holding)
                    self.add_stats("Holdings written to file")
        print("# C-records migration")
        print(f"Time Run: {datetime.isoformat(datetime.utcnow())} UTC")
        print("## C-records migration counters")
        self.print_dict_to_md_table(self.stats, "Measure", "Count")
        print("## Mapped FOLIO Holdings Properties")
        self.print_dict_to_md_table(self.mapped_folio_holdings_fields, "Field", "Count")
        print("## Unmapped FOLIO Holdings Properties")
        self.print_dict_to_md_table(self.unmapped_holdings_fields, "Field", "Count")
        print(f"Created holdings | {len(self.created_holdings)}")
        self.print_migration_report()

    def parse_hlm(self, hsss, holdings):
        return ""
        ret = get_empty_hlm_dict()
        orig = "|".join(hsss)
        if orig:
            r = hsss[0]
            rs = r.split("-")
            rr = []
            for z in rs:
                rr.append(z.split("/")[0])
            r = "-".join(rr)
            for a in hsss[1:]:
                a = a.strip("-")
                if "/" in a and len(a) == 9:
                    a = a.replace("/", "-")
                if "-" in a:
                    b = a.split("-")
                    # Ends with the start of the span
                    prev_year = str(int(b[0].split("/")[0]) - 1)
                    _from = b[0].split("/")[0]
                    _to = b[1].split("/")[-1]
                    if r.endswith(f"-{_from}"):
                        r = r.replace(_from, _to)
                    elif r.endswith(f"-{prev_year}"):
                        r = r.replace(prev_year, _to)
                    elif r.endswith(f"|{prev_year}") or r == prev_year:
                        r = r.replace(prev_year, f"{prev_year}-{_to}")
                    elif r.endswith(f"|{_from}") or r == _from:
                        r = r.replace(_from, f"{_from}-{_to}")
                    else:
                        r = f"{r}|{_from}-{_to}"
                else:
                    prev_year = str(int(a.split("/")[0]) - 1)
                    year = a.split("/")[0]
                    if r.endswith(f"-{prev_year}"):
                        r = r.replace(prev_year, year)
                    elif not r.endswith(f"-{year}") and not r.endswith(prev_year):
                        r = f"{r}|{year}"
                    elif r.endswith(f"|{prev_year}") or r == prev_year:
                        r = f"{r}-{year}"
            if "/" in r:
                print(f"{orig}\t->\t{r}")
            if holdings["instanceId"] not in self.instances:
                path = f'/instance-storage/instances/{holdings["instanceId"]}'
                current_instance = self.folio_client.folio_get_single_object(path)
                print(
                    f'Received {current_instance.get("title", "None")} {holdings["instanceId"]}'
                )
                self.instances[holdings["instanceId"]] = current_instance
            else:
                current_instance = self.instances[holdings["instanceId"]]
            ret["PackageName"] = self.get_folio_location_name(holdings["permanentLocationId"])
            ret["Title"] = current_instance.get("title", "None")
            issn = next(
                (
                    f["value"]
                    for f in current_instance["identifiers"]
                    if f["identifierTypeId"] == "913300b2-03ed-469a-8179-c1092c991227"
                ),
                next((f["value"] for f in current_instance["identifiers"] if
                      f["identifierTypeId"] == "27fd35a6-b8f6-41f2-aa0e-9c663ceb250c"), "", ), )
            print(issn)
            ret["PrintISSN"] = issn
            ret["URL"] = f"http://search.ebscohost.com/login.aspx?authtype=ip,guest&custid=039-820&groupid=main&profid=foliotest&direct=true&scope=site&bquery={issn}&cli0=FC&clv0=Y"
            for a in r.split("|"):
                if "-" in a:
                    b = a.split("-")
                    ret["CustomCoverageBegin"] = f'{ret["CustomCoverageBegin"]}|{b[0]}'
                    ret["CustomCoverageEnd"] = f'{ret["CustomCoverageEnd"]}|{b[1]}'
                else:
                    ret["CustomCoverageBegin"] = f'{ret["CustomCoverageBegin"]}|{a}'
                    ret["CustomCoverageEnd"] = f'{ret["CustomCoverageEnd"]}|{a}'
            ret["CustomCoverageBegin"] = ret["CustomCoverageBegin"].strip("|")
            ret["CustomCoverageEnd"] = ret["CustomCoverageEnd"].strip("|")
            if len(r) > self.longest_statement_len:
                self.longest_statement_len = len(r)
                self.longest_statement = r
            return ret
        return None

    def get_folio_location_name(self, folio_location_id):
        return next(
            (
                location["name"]
                for location in self.folio_client.locations
                if folio_location_id == location["id"]
            ),
            "",
        )

    def get_folio_location(self, iii_location_code):
        loc = next(
            (location for location in self.locations_map if location["iii_code"] == iii_location_code)
        )
        if not loc:
            raise Exception(f"No loc. code found in map for {iii_location_code}")

        if str(loc["barcode_handling"]).startswith("Do not import"):
            self.add_stats("Do not import")
            return ""

        loc_id = next(
            (
                location["id"]
                for location in self.folio_client.locations
                if loc["folio_code"] == location["code"]
            ),
            None,
        )
        if not loc_id:
            raise ValueError(f"No loc. id found in locations for {loc}")
        return loc_id

    def get_location(self, marc_record):
        for f852 in marc_record.get_fields("852"):
            if "b" in f852:
                loc = self.get_folio_location(str(f852["b"]).strip())
                if loc:
                    return loc
        return ""

    def get_instance_id(self, marc_record):
        old_id = marc_record["004"].format_field()[2:-1]
        return (
            self.instance_id_map[old_id]["id"]
            if old_id in self.instance_id_map
            else None
        )

    def get_holdings_statements(
            self, marc_record, field_pattern, field_value, field_textual
    ):
        f863s = marc_record.get_fields(field_value)

        for f in marc_record.get_fields(field_textual):
            yield {"statement": f["a"], "note": ""}, ""

        for t in marc_record.get_fields(field_pattern):
            # wire it up
            link_sequence = t["8"]
            enum_levels = "abcdef"
            chronological_levels = "ijkl"
            linked_fields = [f for f in f863s if f["8"].split(".")[0] == link_sequence]

            if not any(linked_fields):
                self.add_to_migration_report(
                    "Missing linked fields",
                    f"Missing linked fields for {t} in {marc_record['001']}",
                )
            else:
                for linked_field in linked_fields:
                    hlm_stmt = ""
                    stmt = ""
                    note = ""
                    _from = ""
                    _to = ""
                    for enum_level in [el for el in enum_levels if el in linked_field]:
                        desc = t[enum_level] or ""
                        desc = desc if "(" not in desc else ""
                        if linked_field[enum_level]:
                            val, *val_rest = linked_field[enum_level].split("-")
                            _from = f"{_from}{(':' if _from else '')}{desc}{val}"
                            temp_to = "".join(val_rest)
                            if temp_to.strip():
                                _to = f"{_to}{(':' if _to else '')}{desc}{temp_to}"

                    cron_from = ""
                    cron_to = ""
                    year = False
                    for chron_level in [cl for cl in chronological_levels if cl in linked_field]:
                        desc = t[chron_level] or ""
                        if linked_field[chron_level]:
                            if chron_level == "i" and desc == "(year)":
                                hlm_stmt = linked_field[chron_level]
                            if desc == "(year)":
                                year = True
                            val, *val_rest = linked_field[chron_level].split("-")
                            if desc == "(month)":
                                try:
                                    val = calendar.month_abbr[int(val)]
                                except Exception:
                                    val = val
                                if "".join(val_rest):
                                    try:
                                        val_rest = calendar.month_abbr[
                                            int("".join(val_rest))
                                        ]
                                    except Exception:
                                        val_rest = val_rest
                                if year:
                                    cron_from = f"{val} {cron_from}  "
                                    cron_to = f"{''.join(val_rest)} {cron_to}"
                            else:
                                if "season" in desc:
                                    val = get_season(val)
                                cron_from = f"{cron_from} {val} "
                                cron_to = f"{cron_to} {''.join(val_rest)}"
                    cron_from = cron_from.strip()
                    cron_to = cron_to.strip()
                    _from = _from.strip()
                    _to = _to.strip()
                    if cron_from:
                        _from = f"{_from} ({cron_from})"
                    if _to and cron_to:
                        _to = f"{_to} ({cron_to})"
                    if _to and cron_from and not cron_to:
                        _to = f"{_to} ({cron_from})"
                    if _from:
                        stmt = f"{_from}-{_to}"
                    """match = re.match(r"^\d{4}\/\d{4}-$", stmt.strip())
                    if match:
                        stmt = stmt.replace("-", "")"""
                    stmt = stmt.strip("-")
                    if "w" in linked_field and linked_field["w"] == "g":
                        stmt = f"{stmt} gaps. "
                    if "z" in linked_field:
                        note = f"{note}, {linked_field['z']} "
                    if "x" in linked_field:
                        note = f"{note}, {linked_field['x']} "
                    stmt = re.sub(" +", " ", stmt)
                    yield {"statement": stmt.strip(), "note": note}, hlm_stmt

    def merge_holding(self, holdings_record):
        # Todo: move to central, shared class
        key = to_key(holdings_record)
        self.created_holdings[key]["notes"].extend(holdings_record["notes"])
        self.created_holdings[key]["notes"] = deduplicate(
            self.created_holdings[key]["notes"]
        )
        self.created_holdings[key]["holdingsStatements"].extend(
            holdings_record["holdingsStatements"]
        )
        self.created_holdings[key]["holdingsStatements"] = deduplicate(
            self.created_holdings[key]["holdingsStatements"]
        )
        self.created_holdings[key]["formerIds"].extend(holdings_record["formerIds"])

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,
                                     "records_file", "Path to the file", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Path to the file", "DirChooser"
                                     )
        ServiceTaskBase.add_argument(parser, "instance_id_map_path", "File with instance IDs", "FileChooser")
        ServiceTaskBase.add_argument(parser, "location_map_path", "File with instance IDs", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser,
                                         "records_file", help="path to folder with files to map")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="path to results file")
        ServiceTaskBase.add_cli_argument(parser, "instance_id_map_path", help="path to results file")
        ServiceTaskBase.add_cli_argument(parser, "location_map_path", help="path to location map file")

    def validate(self, folio_object):
        for key, value in folio_object.items():
            if isinstance(value, str) and any(value):
                self.add_stats(key)
            if isinstance(value, list) and any(value):
                self.add_stats(key)

    def count_unmapped_fields(self, folio_object):
        schema_properties = self.holdings_schema["properties"].keys()
        unmatched_properties = (
            p for p in schema_properties if p not in folio_object.keys()
        )
        for p in unmatched_properties:
            self.add_stats(p)


def write_hlm_export(rows, dirname):
    keys = get_empty_hlm_dict().keys()
    csvfilename = os.path.join(dirname, "hlm_export.tsv")
    with open(csvfilename, "w") as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter="\t")
        dict_writer.writeheader()
        dict_writer.writerows(rows)


def get_empty_hlm_dict():
    return {
        "KBID": "",
        "Title": "",
        "AlternateTitle": "",
        "PackageName": "",
        "URL": "",
        "ProxiedURL": "",
        "Publisher": "",
        "Edition": "",
        "Author": "",
        "Editor": "",
        "Illustrator": "",
        "PrintISSN": "",
        "OnlineISSN": "",
        "PrintISBN": "",
        "OnlineISBN": "",
        "DOI": "",
        "PeerReviewed": "",
        "ManagedCoverageBegin": "",
        "ManagedCoverageEnd": "",
        "CustomCoverageBegin": "",
        "CustomCoverageEnd": "",
        "CoverageStatement": "",
        "Embargo": "",
        "CustomEmbargo": "",
        "Description": "",
        "Subject": "",
        "ResourceType": "",
        "PackageContentType": "",
        "CreateCustom": "",
        "HideOnPublicationFinder": "",
        "Delete": "",
        "OrderedThroughEBSCO": "",
        "IsCustom": "",
        "UserDefinedField1": "",
        "UserDefinedField2": "",
        "UserDefinedField3": "",
        "UserDefinedField4": "",
        "UserDefinedField5": "",
        "PackageType": "",
        "AllowEbscoToAddNewTitles": "",
    }


def write_to_file(file, folio_record):
    """Writes record to file"""
    file.write("{}\n".format(json.dumps(folio_record)))


def timings(t0, t0func, num_objects):
    avg = num_objects / (time.time() - t0)
    elapsed = time.time() - t0
    elapsed_func = num_objects / (time.time() - t0func)
    return (f"Objects processed: {num_objects}\tTotal elapsed: {elapsed}\t"
            f"Average per object: {avg:.2f}\tElapsed this time: {elapsed_func:.2f}")


def get_call_number(marc_record):
    for f852 in marc_record.get_fields("852"):
        if "h" in f852 or "i" in f852:
            return " ".join(f852.get_subfields(*"hi"))
    return ""


def get_notes(marc_record):
    for f852 in marc_record.get_fields("852"):
        if "z" in f852:
            yield {
                "note": f852["z"],
                "staffOnly": False,
                "holdingNoteTypeId": "085881c1-d5db-48db-0314-ef56e5f83a95",  # public note
            }


def to_key(holding):
    # Todo: move to central, shared class
    try:
        """creates a key of key values in holding record
        to determine uniquenes"""
        call_number = (
            "".join(holding["callNumber"].split())
            if "callNumber" in holding
            else ""
        )
        return "-".join(
            [holding["instanceId"], call_number, holding["permanentLocationId"], ""]
        )
    except Exception as ee:
        print(holding)
        raise ee


def deduplicate(list_of_dicts):
    return [dict(t) for t in {tuple(d.items()) for d in list_of_dicts}]


def get_season(val):
    try:
        val = int(val)
        if val == 21:
            return "Spring"
        elif val == 22:
            return "Summer"
        elif val == 23:
            return "Fall"
        elif val == 24:
            return "Winter"
        else:
            return val
    except Exception:
        return val
