import csv
import json
import logging
import re
import uuid
from datetime import datetime

from dateutil.parser import parse
from typing import Dict

from folioclient import FolioClient

from user_migration.mappers.mapper_base import MapperBase


class Default(MapperBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.args = args
        self.user_schema = MapperBase.get_user_schema()
        self.ids_dict: Dict[str, set] = {}
        self.use_map = True

    def do_map(self, legacy_user, user_map):
        # raise NotImplementedError("Create ID-Legacy ID Mapping file!")
        # raise NotImplementedError("Check for ID duplicates (barcodes, externalsystemID:s, usernames, emails?, ")
        folio_user = self.instantiate_user()
        self.add_to_migration_report("Users per patron type", str(self.get_prop(legacy_user, user_map, "patronGroup")))
        for prop_name, prop in self.user_schema["properties"].items():
            if prop.get("description", "") == "Deprecated":
                self.report_folio_mapping(f"{prop_name} (deprecated)", False, True)
                continue
            if prop_name == "metadata":
                self.report_folio_mapping(f"{prop_name}", True, False)
                continue
            if prop["type"] == "object":
                folio_user[prop_name] = {}
                prop_key = prop_name
                if "properties" in prop:
                    for sub_prop_name, sub_prop in prop["properties"].items():
                        sub_prop_key = prop_key + "." + sub_prop_name
                        if "properties" in sub_prop:
                            for sub_prop_name2, sub_prop2 in sub_prop["properties"].items():
                                sub_prop_key2 = sub_prop_key + "." + sub_prop_name2
                                if sub_prop2["type"] == "array":
                                    logging.warning(f"Array: {sub_prop_key2} ")
                        elif sub_prop["type"] == "array":
                            folio_user[prop_name][sub_prop_name] = []
                            for i in range(0, 5):
                                if sub_prop["items"]["type"] == "object":
                                    temp = {}
                                    for sub_prop_name2, sub_prop2 in sub_prop["items"]["properties"].items():
                                        temp[sub_prop_name2] = self.get_prop(legacy_user, user_map,
                                                                             sub_prop_key + "." + sub_prop_name2, i)
                                    if all(value == "" for key, value in temp.items() if
                                           key not in ["id", "primaryAddress", "addressTypeId"]):
                                        continue
                                    folio_user[prop_name][sub_prop_name].append(temp)
                                else:
                                    mkey = sub_prop_key + "." + sub_prop_name2
                                    folio_user[prop_name][sub_prop_name] = self.get_prop(legacy_user,
                                                                                         mkey,
                                                                                         i)

                        else:
                            folio_user[prop_name][sub_prop_name] = self.get_prop(legacy_user, user_map, sub_prop_key)

            elif prop["type"] == "array":
                # handle departments
                self.report_folio_mapping(f"Unhandled array: {prop_name}", False)

            else:
                self.map_basic_props(legacy_user, user_map, prop_name, folio_user)
                """ elif prop == "customFields":
                    custom_fields = [c for c in legacy_user if c.startswith("customField")]
                    if any(custom_fields):
                        for custom_field in custom_fields:
                            folio_user["customFields"][custom_field.split('.')[1]] = legacy_user[custom_field]
                            self.add_to_migration_report("General",
                                                         f"Custom field {custom_field.split('.')[1]} added")
                            self.report_legacy_mapping(prop, True, False)
                            self.report_folio_mapping(prop, True, False) """

            """ for prop in legacy_user:
            if prop not in mapped_legacy_props:
                if legacy_user[prop].strip():
                    self.report_legacy_mapping(f"{prop}", False, False)
                else:
                    self.report_legacy_mapping(f"{prop}", False, True)"""

        # folio_user['patronGroup'] = self.get_prop(legacy_user, 'patronGroup')
        # self.add_to_migration_report("Users by FOLIO Patron Group", folio_user['patronGroup'])
        # self.handle_addresses(folio_user, legacy_user_dict)
        # self.validate(folio_user)
        folio_user["personal"]["preferredContactTypeId"] = "Email"
        folio_user["active"] = True
        del folio_user["personal"]["preferredFirstName"]
        del folio_user["tags"]

        return folio_user

    def map_basic_props(self, legacy_user, user_map, prop, folio_user):
        if self.has_property(legacy_user, user_map, prop):  # is there a match in the csv?
            if self.get_prop(legacy_user, user_map, prop).strip():
                folio_user[prop] = self.get_prop(legacy_user, user_map, prop)
                self.report_legacy_mapping(self.legacy_property(user_map, prop), True, False)
                self.report_folio_mapping(prop, True, False)
            else:  # Match but empty field. Lets report this
                self.report_legacy_mapping(self.legacy_property(user_map, prop), True, True)
                self.report_folio_mapping(prop, True, True)
        else:
            self.report_folio_mapping(prop, False)

    def get_users(self, source_file, file_format: str):
        address_fields = ["countryId", "addressLine1", "addressLine2", "city", "region", "postalCode",
                          "addressTypeId", "primaryAddress"]
        csv.register_dialect("tsv", delimiter="\t")
        if file_format == "tsv":
            reader = csv.DictReader(source_file, dialect='tsv')
        else:  # Assume csv
            reader = csv.DictReader(source_file)
        current_user = {}
        current_user_id = ""
        for row in reader:
            # return [row]
            yield row

    def get_prop(self, legacy_user, user_map, folio_prop_name, i=0):
        if self.use_map:
            legacy_user_key = next((k["legacy_field"] for k
                                    in user_map["data"]
                                    if k["folio_field"].replace(f"[{i}]", "") == folio_prop_name), "")
            value = next(
                (k.get("value", "")
                 for k in user_map["data"]
                 if k["folio_field"].replace(f"[{i}]", "") == folio_prop_name), ""
            )
            if value:
                self.add_to_migration_report("Default values added", f"{value} added to {folio_prop_name}")
                return value

            if folio_prop_name == "personal.addresses.id":
                return "not needed"
            elif folio_prop_name == "expirationDate" or folio_prop_name == "enrollmentDate":
                try:
                    format_date = parse(legacy_user.get(legacy_user_key), fuzzy=True)
                    return format_date.isoformat()
                except Exception as ee:
                    logging.error(f"expiration date {legacy_user.get(legacy_user_key)} could not be parsed")
                    return datetime.utcnow().isoformat()
            elif folio_prop_name.strip() == "personal.addresses.primaryAddress":
                return i == 0  # The first address in the mapping file (the one with [0]) will be primary
            elif folio_prop_name == "personal.addresses.addressTypeId":
                try:
                    address_type_id = user_map["addressTypes"][i]
                    self.report_folio_mapping(f"{folio_prop_name}", True, False)
                    return address_type_id
                except KeyError as key_error:
                    # logging.error(f"Key error: {key_error} i:{i}")
                    # json.dumps(user_map, indent=4)
                    return ""
                except IndexError:
                    return ""
            elif legacy_user_key:
                self.report_folio_mapping(f"{folio_prop_name}", True, False)
                return legacy_user.get(legacy_user_key, "")
            else:
                self.report_folio_mapping(f"{folio_prop_name}", False, False)
                return ""
        else:
            self.report_folio_mapping(f"{folio_prop_name}", True, False)
            return legacy_user[folio_prop_name]

    def has_property(self, user, user_map, folio_prop_name):
        if self.use_map:
            user_key = next((k["legacy_field"] for k in user_map["data"] if k["folio_field"] == folio_prop_name),
                            "")
            return user_key and user_key not in ["", "Not mapped"] and user.get(user_key, "")
        else:
            return folio_prop_name in user

    def legacy_property(self, user_map, folio_prop_name):
        if self.use_map:
            value = next(
                (k.get("value", "") for k in user_map["data"] if k["folio_field"] == folio_prop_name), "")
            if value:
                self.add_to_migration_report("Default values added", f"{value} added to {folio_prop_name}")
                return value
            return next(k["legacy_field"] for k in user_map["data"] if k["folio_field"] == folio_prop_name)
        else:
            return folio_prop_name
