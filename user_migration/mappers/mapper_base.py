import json
import uuid
from abc import abstractmethod
import requests
from folioclient import FolioClient
import os


class MapperBase():
    def __init__(self, folio_client: FolioClient):
        self.stats = {}
        self.migration_report = {}
        self.folio_client = folio_client
        self.mapped_folio_fields = {}
        self.mapped_legacy_fields = {}
        self.user_schema = self.get_user_schema()

    def print_mapping_report(self, total_records):
        print('\n## Mapped FOLIO fields')
        d_sorted = {k: self.mapped_folio_fields[k] for k in sorted(self.mapped_folio_fields)}
        print(f"FOLIO Field | Mapped | Empty | Unmapped")
        print("--- | --- | --- | ---:")
        for k, v in d_sorted.items():
            unmapped = total_records - v[0]
            mapped = v[0] - v[1]
            unmapped_per = "{:.1%}".format(unmapped / total_records)
            mp = mapped / total_records
            mapped_per = "{:.0%}".format(mp if mp > 0 else 0)
            print(f"{k} | {mapped if mapped > 0 else 0} ({mapped_per}) | {v[1]} | {unmapped}")
        print('\n## Mapped Legacy fields')
        d_sorted = {k: self.mapped_legacy_fields[k] for k in sorted(self.mapped_legacy_fields)}
        print(f"Legacy Field | Mapped | Empty | Unmapped")
        print("--- | --- | --- | ---:")
        for k, v in d_sorted.items():
            unmapped = total_records - v[0]
            mapped = v[0] - v[1]
            unmapped_per = "{:.1%}".format(unmapped / total_records)
            mp = mapped / total_records
            mapped_per = "{:.0%}".format(mp if mp > 0 else 0)
            print(f"{k} | {mapped if mapped > 0 else 0} ({mapped_per}) | {v[1]} | {unmapped}")

    def report_legacy_mapping(self, field_name, was_mapped, was_empty=False):
        if field_name not in self.mapped_legacy_fields:
            self.mapped_legacy_fields[field_name] = [int(was_mapped), int(was_empty)]
        else:
            self.mapped_legacy_fields[field_name][0] += int(was_mapped)
            self.mapped_legacy_fields[field_name][1] += int(was_empty)

    def report_folio_mapping(self, field_name, was_mapped, was_empty=False):
        if field_name not in self.mapped_folio_fields:
            self.mapped_folio_fields[field_name] = [int(was_mapped), int(was_empty)]
        else:
            self.mapped_folio_fields[field_name][0] += int(was_mapped)
            self.mapped_folio_fields[field_name][1] += int(was_empty)

    def instantiate_user(self):
        folio_user = {"metadata": self.folio_client.get_metadata_construct(),
                      "id": str(uuid.uuid4()),
                      "type": "object",
                      "personal": {},
                      "customFields": {}}
        self.report_folio_mapping("id", True)
        self.report_folio_mapping("metadata", True)
        return folio_user

    def validate(self, folio_user):
        failures = []
        self.add_to_migration_report("Number of addresses per user", len(folio_user["personal"].get("addresses", [])))
        req_fields = ['username', 'externalSystemId']
        for req in req_fields:
            if req not in folio_user:
                failures.append(req)
                self.add_to_migration_report(
                    "Failed records that needs to get fixed",
                    f"Required field {req} is missing from {folio_user['username']}",
                )
        if not folio_user['personal'].get('lastName', ""):
            failures.append('lastName')
            self.add_to_migration_report(
                "Failed records that needs to get fixed",
                f"Required field personal.lastName is missing from {folio_user['username']}",
            )
        if len(failures) > 0:
            self.add_to_migration_report("User validation", "Total failed users")
            for failure in failures:
                self.add_to_migration_report("User validation", f"{failure}")
            raise ValueError(
                f"Record {folio_user['username']} failed validation {failures}"
            )

    def write_migration_report(self, other_report=None):
        for a in self.migration_report:
            print('')
            print(f"## {a} - {len(self.migration_report[a])} things")
            print(f"Measure | Count")
            print("--- | ---:")
            b = self.migration_report[a]
            sortedlist = [(k, b[k]) for k in sorted(b, key=as_str)]
            for b in sortedlist:
                print(f"{b[0]} | {b[1]}")

    @staticmethod
    def print_dict_to_md_table(my_dict, h1="", h2=""):
        d_sorted = {k: my_dict[k] for k in sorted(my_dict)}
        print(f"{h1} | {h2}")
        print("--- | ---:")
        for k, v in d_sorted.items():
            print(f"{k} | {v}")

    def add_to_migration_report(self, header, measure_to_add):
        if header not in self.migration_report:
            self.migration_report[header] = {}
        if measure_to_add not in self.migration_report[header]:
            self.migration_report[header][measure_to_add] = 1
        else:
            self.migration_report[header][measure_to_add] += 1

    @abstractmethod
    def do_map(self):
        raise NotImplementedError

    @abstractmethod
    def get_users(self, source_file):
        raise NotImplementedError

    @staticmethod
    def get_user_schema():
        url = "https://raw.githubusercontent.com/folio-org/mod-users/master/ramls/userdata.json"
        req = requests.get(url)
        return json.loads(req.text)


def as_str(s):
    try:
        return str(s), ''
    except ValueError:
        return '', s