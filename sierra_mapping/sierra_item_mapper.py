import json
import re
import traceback
import uuid
from abc import ABC

from folioclient import FolioClient

from helpers.custom_exceptions import *
from user_migration.mappers.mapper_base import MapperBase


class SierraItemTransformer(MapperBase, ABC):
    def __init__(self, folio_client: FolioClient, instance_id_map, loan_type_map, material_type_map, location_map,
                 call_number_type_map):
        super().__init__(folio_client)

        # Setup arguments
        self.loan_type_map = loan_type_map
        self.instance_id_map = instance_id_map
        self.material_type_map = material_type_map
        self.location_map = location_map
        self.call_number_type_map = call_number_type_map

        # Fetch schemas
        self.item_schema = self.folio_client.get_item_schema()
        self.holdings_schema = self.folio_client.get_holdings_schema()

        # the mapping stuff
        print("Fetching callnumber types...")
        self.folio_call_number_types = list(
            self.folio_client.folio_get_all("/call-number-types", "callNumberTypes")
        )
        self.call_number_type_keys = []
        self.default_call_number_type_id = ""
        self.setup_call_number_type_mappings()

        print("Fetching loan types...")
        self.folio_loan_types = list(
            self.folio_client.folio_get_all("/loan-types", "loantypes")
        )
        self.default_loan_type_id = ""
        self.loan_type_keys = []
        self.setup_loan_type_mappings()

        print("Fetching material types...")
        self.folio_material_types = list(
            self.folio_client.folio_get_all("/material-types", "mtypes")
        )
        self.default_material_type_id = ""
        self.material_type_keys = []
        self.setup_material_type_mappings()

        print("Fetching locations...")
        self.location_keys = []
        self.default_location_id = ""
        self.setup_location_mappings(location_map)

        # The rest
        self.holdings = {}  # map of created holdings
        self.item_id_map = {}
        self.circulation_note_map = {}

        print("Done init.")

    def transform(self, sierra_item: dict, items_file):
        holding = self.convert_to_holding(sierra_item)
        holding_key = self.to_key(holding)
        existing_holding = self.holdings.get(holding_key, None)
        if not existing_holding:
            self.add_stats(self.stats, "Unique Holdings created from Items")
            self.holdings[self.to_key(holding)] = holding
        else:
            self.add_stats(self.stats, "Holdings Already Created from Item")
            self.merge_holding(holding)

        item = self.convert_to_item(sierra_item, holding)
        item["holdingsRecordId"] = self.holdings[self.to_key(holding)]["id"]
        self.write_object(item, items_file)

    def convert_to_item(self, sierra_item, holding):
        new_item = {
            "id": str(uuid.uuid4()),
            "holdingsRecordId": holding["id"],
            "barcode": sierra_item.get("barcode", ""),
            "volume": next(get_varfields_no_subfield(sierra_item, "v"), ""),
            "formerIds": [get_varfield(sierra_item, "i", "a")],
            "notes": list(self.get_notes(sierra_item)),
            "circulationNotes": list(self.get_circ_notes(sierra_item)),
            "status": self.get_status(sierra_item),
            "materialTypeId": self.get_material_type_id(sierra_item, sierra_item["id"]),
            "permanentLoanTypeId": self.get_loan_type_id(sierra_item, sierra_item["id"]),
            "metadata": self.folio_client.get_metadata_construct(),
        }
        new_item["metadata"]["createdDate"] = sierra_item["fixedFields"]["83"]["value"]
        new_item["metadata"]["updatedDate"] = sierra_item["fixedFields"]["84"]["value"]

        # self.handle_sierra_status(sierra_item, new_item)
        map_struct = {
            "id": new_item["id"],
            "item_type_id": new_item["materialTypeId"],
            "loan_type_id": new_item["permanentLoanTypeId"],
            "location_id": holding["permanentLocationId"],
        }
        self.item_id_map[sierra_item["id"]] = map_struct
        return new_item

    def convert_to_holding(self, sierra_item):
        if len(sierra_item["bibIds"]) > 1:
            self.add_stats(self.stats, "Item connected to more than one Bib/Instance")
        sierra_bib_id = next(f for f in sierra_item["bibIds"])
        if ',' in sierra_bib_id:
            sierra_bib_id = sierra_bib_id.split(',')[0]
        # sierra_bib_id = re.sub(r"^\.b|b", "", sierra_bib_id)
        print(sierra_bib_id)
        new_instance_id = self.instance_id_map.get(sierra_bib_id, {}).get("folio_id", "")
        sierra_bib_id = sierra_bib_id

        if not new_instance_id:
            self.add_stats(self.stats, f"Bib Id not in list of migrated records")
            self.add_to_migration_report(
                "Sierra Items without migrated Instances. Must be corrected",
                f"Sierra Bib Id {sierra_bib_id} missing in migrated bibs for Sierra Item {sierra_item['id']}",
            )
            print(f"{sierra_bib_id} {next(iter(self.instance_id_map.items()))}")
            raise TransformationCriticalDataError(
                f'Missing Instances in map - Sierra Item {sierra_item["id"]} with bibIds:{sierra_item["bibIds"]}'
            )
        else:
            self.add_stats(self.stats, f"Mapped instance ids")

        new_holding = {
            "id": str(uuid.uuid4()),
            # holdingsTypeId
            "formerIds": list(),
            "instanceId": new_instance_id,
            "permanentLocationId": self.get_location_id(sierra_item, sierra_item["id"]),
            "callNumberTypeId": self.default_call_number_type_id,
            "callNumber": sierra_item.get("callNumber", ""),
            "callNumberSuffix": get_varfield(sierra_item, "c", "l", True).strip(),
            "notes": list(),
            "holdingsStatements": list(),
            "metadata": self.folio_client.get_metadata_construct(),
        }
        new_holding["metadata"]["createdDate"] = sierra_item["fixedFields"]["83"][
            "value"
        ]
        new_holding["metadata"]["updatedDate"] = sierra_item["fixedFields"]["84"][
            "value"
        ]
        return new_holding

    def get_notes(self, sierra_item):
        check_outs = int(sierra_item["fixedFields"].get("76", {}).get("value", 0))
        renewals = int(sierra_item["fixedFields"].get("77", {}).get("value", 0))
        notes_y = next(get_varfields_no_subfield(sierra_item, "y"), "")
        if len(sierra_item["bibIds"]) > 1:
            ids = [
                f"{i} ({self.get_folio_instance_id(i)})" for i in sierra_item["bibIds"]
            ]
            self.add_stats(self.stats, "Notes added to items")
            yield {
                "itemNoteTypeId": "8d0a5eca-25de-4391-81a9-236eeefdd20b",
                "note": f"Bound-with Instance(s): {json.dumps(ids)}",
                "staffOnly": True,
            }
        if check_outs + renewals > 0:
            self.add_stats(self.stats, "Notes added to items")
            yield {
                "itemNoteTypeId": "8d0a5eca-25de-4391-81a9-236eeefdd20b",
                "note": (
                    f"Sierra checkouts: {check_outs}, Sierra renewals: {renewals}"
                    f", Old count: {notes_y}"
                ),
                "staffOnly": True,
            }
        for note_x in get_varfields_no_subfield(sierra_item, "x"):
            if note_x:
                self.add_stats(self.stats, "Notes added to items")
                yield {
                    "itemNoteTypeId": "8d0a5eca-25de-4391-81a9-236eeefdd20b",
                    "note": note_x,
                    "staffOnly": True,
                }
        for note_a in get_varfields_no_subfield(sierra_item, "a"):
            if note_a:
                self.add_stats(self.stats, "Notes added to items")
                yield {
                    "itemNoteTypeId": "8d0a5eca-25de-4391-81a9-236eeefdd20b",
                    "note": note_a,
                    "staffOnly": True,
                }
        for note_n in get_varfields_no_subfield(sierra_item, "n"):
            if note_n:
                self.add_stats(self.stats, "Notes added to items")
                yield {
                    "itemNoteTypeId": "8d0a5eca-25de-4391-81a9-236eeefdd20b",
                    "note": note_n,
                    "staffOnly": False,
                }

    def get_folio_instance_id(self, bib_id: str):
        return self.instance_id_map.get(bib_id, {}).get("id", "")

    def get_status(self, sierra_item):
        sierra_code = sierra_item.get("status", {}).get("code", "")
        self.add_to_migration_report("Legacy Status mappings", f"{sierra_code} -> Available")
        return {"name": "Available"}

    @staticmethod
    def write_object(obj, file):
        # TODO: Move to interface or parent class
        file.write("{}\t{}\n".format(obj["id"], json.dumps(obj)))

    @staticmethod
    def to_key(holding):
        """creates a key if key values in holding record
        to determine uniquenes"""
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

    @staticmethod
    def add_stats(stats, measure_to_add):
        if measure_to_add not in stats:
            stats[measure_to_add] = 1
        else:
            stats[measure_to_add] += 1

    def get_circ_notes(self, sierra_item):
        source = {
            "id": self.folio_client.current_user,
            "personal": {"lastName": "Sierra", "firstName": "Migrated"},
        }
        for note_m in get_varfields_no_subfield(sierra_item, "m"):
            if note_m and len(note_m) > 5:
                self.add_to_migration_report("Circulation notes", "From Varfield m")
                yield {
                    "id": str(uuid.uuid4()),
                    "noteType": "Check in",
                    "source": source,
                    "note": note_m,
                    "staffOnly": True,
                    "date": "2019-06-29T13:37:01.071+0000",
                }
                yield {
                    "id": str(uuid.uuid4()),
                    "noteType": "Check out",
                    "source": source,
                    "note": note_m,
                    "staffOnly": True,
                    "date": "2019-06-29T13:37:01.071+0000",
                }
        note_97 = sierra_item["fixedFields"].get("97", {}).get("value")
        if note_97:
            self.add_to_migration_report("Circulation notes", "From fixed field 97")
            self.add_stats(self.stats, f"Items with Circ notes - Fixed 97")
            yield {
                "id": str(uuid.uuid4()),
                "noteType": "Check in",
                "source": source,
                "note": note_97,
                "staffOnly": True,
                "date": "2019-06-29T13:37:01.071+0000",
            }
            yield {
                "id": str(uuid.uuid4()),
                "noteType": "Check out",
                "source": source,
                "note": note_97,
                "staffOnly": True,
                "date": "2019-06-29T13:37:01.071+0000",
            }

    def merge_holding(self, holdings_record):
        # TODO: Move to interface or parent class
        key = self.to_key(holdings_record)
        self.holdings[key]["notes"].extend(holdings_record["notes"])
        self.holdings[key]["notes"] = dedupe(self.holdings[key]["notes"])
        self.holdings[key]["holdingsStatements"].extend(
            holdings_record["holdingsStatements"]
        )
        self.holdings[key]["holdingsStatements"] = dedupe(
            self.holdings[key]["holdingsStatements"]
        )
        self.holdings[key]["formerIds"].extend(holdings_record["formerIds"])

    def setup_call_number_type_mappings(self):
        # Loan types
        for idx, call_number_type_mapping in enumerate(self.call_number_type_map):
            try:
                if idx == 1:
                    self.call_number_type_keys = list(
                        [
                            k
                            for k in call_number_type_mapping.keys()
                            if k not in ["folio_code", "folio_id", "folio_name"]
                        ]
                    )
                    print(self.call_number_type_keys)
                if any(m for m in call_number_type_mapping.values() if m == "*"):
                    t = self.get_ref_data_tuple_by_name(
                        self.folio_call_number_types,
                        "callnumbers",
                        call_number_type_mapping["folio_name"],
                    )
                    if t:
                        self.default_call_number_type_id = t[0]
                        print(
                            f'Set {call_number_type_mapping["folio_name"]} as default callnumber type mapping'
                        )
                    else:
                        raise TransformationProcessError(
                            "No Default call_number type set up in map."
                            "Add a row to mapping file with *:s and a valid call_number type"
                        )
                else:
                    call_number_type_mapping[
                        "folio_id"
                    ] = self.get_ref_data_tuple_by_name(
                        self.folio_call_number_types,
                        "callnumbers",
                        call_number_type_mapping["folio_name"],
                    )[
                        0
                    ]
            except Exception as exception:
                if isinstance(exception, TransformationProcessError):
                    raise exception
                else:
                    print(json.dumps(self.call_number_type_map, indent=4))
                    print(exception)
                    raise TransformationProcessError(
                        f"{call_number_type_mapping['folio_name']} could not be found in FOLIO"
                    )
        if not self.default_call_number_type_id:
            raise TransformationProcessError(
                "No Default Callnumber type set up in map."
                "Add a row to mapping file with *:s and a valid callnumber type"
            )
        print(
            f"loaded {idx} mappings for {len(self.folio_call_number_types)} loan types in FOLIO"
        )

    def setup_loan_type_mappings(self):
        # Loan types
        for idx, loan_type_mapping in enumerate(self.loan_type_map):
            try:
                if idx == 1:
                    self.loan_type_keys = list(
                        [
                            k
                            for k in loan_type_mapping.keys()
                            if k not in ["folio_code", "folio_id", "folio_name"]
                        ]
                    )
                if any(m for m in loan_type_mapping.values() if m == "*"):
                    t = self.get_ref_data_tuple_by_name(
                        self.folio_loan_types,
                        "loan_types",
                        loan_type_mapping["folio_name"],
                    )
                    if t:
                        self.default_loan_type_id = t[0]
                        print(
                            f'Set {loan_type_mapping["folio_name"]} as default Loantype mapping'
                        )
                    else:
                        raise TransformationProcessError(
                            "No Default Loan type set up in map."
                            "Add a row to mapping file with *:s and a valid loan type"
                        )
                else:
                    loan_type_mapping["folio_id"] = self.get_ref_data_tuple_by_name(
                        self.folio_loan_types,
                        "loan_types",
                        loan_type_mapping["folio_name"],
                    )[0]
            except Exception as exception:
                if isinstance(exception, TransformationProcessError):
                    raise exception
                else:
                    print(exception)
                    print(json.dumps(self.loan_type_map, indent=4))
                    raise TransformationProcessError(
                        f"{loan_type_mapping['folio_name']} could not be found in FOLIO"
                    )
        if not self.default_loan_type_id:
            raise TransformationProcessError(
                "No Default Loan type set up in map."
                "Add a row to mapping file with *:s and a valid loan type"
            )
        print(
            f"loaded {idx} mappings for {len(self.folio_loan_types)} loan types in FOLIO"
        )

    def setup_material_type_mappings(self):
        # Material types
        for idx, mat_mapping in enumerate(self.material_type_map):
            try:
                if idx == 1:
                    self.material_type_keys = list(
                        [
                            k
                            for k in mat_mapping.keys()
                            if k not in ["folio_code", "folio_id", "folio_name"]
                        ]
                    )
                if any(m for m in mat_mapping.values() if m == "*"):
                    t = self.get_ref_data_tuple_by_name(
                        self.folio_material_types,
                        "mat_types",
                        mat_mapping["folio_name"],
                    )
                    if t:
                        self.default_material_type_id = t[0]
                        print(
                            f'Set {mat_mapping["folio_name"]} as default material type mapping'
                        )
                    else:
                        raise TransformationProcessError(
                            "No Default Material type set up in map."
                            "Add a row to mapping file with *:s and a valid Material type"
                        )
                else:
                    t = self.get_ref_data_tuple_by_name(
                        self.folio_material_types,
                        "mat_types",
                        mat_mapping["folio_name"],
                    )
                    mat_mapping["folio_id"] = t[0]
            except Exception as exception:
                if isinstance(exception, TransformationProcessError):
                    raise exception
                else:
                    print(exception)
                    traceback.print_exc()
                    raise TransformationProcessError(
                        f"Mapping value {mat_mapping['folio_name']} could not be found in FOLIO"
                    )
        if not self.default_material_type_id:
            raise TransformationProcessError(
                "No Default Material type set up in map."
                "Add a row to mapping file with *:s and a valid Material type"
            )
        print(
            f"loaded {idx} mappings for {len(self.folio_material_types)} material types in FOLIO"
        )

    def setup_location_mappings(self, location_map):
        # Locations
        for idx, loc_map in enumerate(location_map):
            if idx == 1:
                self.location_keys = list(
                    [
                        k
                        for k in loc_map.keys()
                        if k not in ["folio_code", "folio_id", "folio_name"]
                    ]
                )
            if any(m for m in loc_map.values() if m == "*"):
                t = self.get_ref_data_tuple_by_code(
                    self.folio_client.locations, "locations", loc_map["folio_code"]
                )
                if t:
                    self.default_location_id = t[0]
                    print(f'Set {loc_map["folio_code"]} as default location')
                else:
                    raise TransformationProcessError(
                        f"Default location {loc_map['folio_code']} not found in folio. "
                        "Change default code"
                    )
            else:
                t = self.get_ref_data_tuple_by_code(
                    self.folio_client.locations, "locations", loc_map["folio_code"]
                )
                if t:
                    loc_map["folio_id"] = t[0]
                else:
                    raise Exception(
                        f"Location code {loc_map['folio_code']} from map not found in FOLIO"
                    )

        if not self.default_location_id:
            raise TransformationProcessError(
                "No Default Location set up in map. "
                "Add a row to mapping file with *:s and a valid Location code"
            )
        print(
            f"loaded {idx} mappings for {len(self.folio_client.locations)} locations in FOLIO"
        )

    def get_item_level_call_number_type_id(self, legacy_item, id_or_index):
        return self.get_mapped_value(
            "Callnumber type",
            legacy_item,
            self.call_number_type_keys,
            self.call_number_type_map,
            self.default_call_number_type_id,
            "folio_name", id_or_index
        )

    def get_loan_type_id(self, legacy_item: dict, id_or_index):
        return self.get_mapped_value(
            "Loan type",
            legacy_item,
            self.loan_type_keys,
            self.loan_type_map,
            self.default_loan_type_id,
            "folio_name",
            id_or_index
        )

    def get_material_type_id(self, legacy_item: dict, id_or_index):
        return self.get_mapped_value(
            "Material type",
            legacy_item,
            self.material_type_keys,
            self.material_type_map,
            self.default_material_type_id,
            "folio_name",
            id_or_index
        )

    def get_location_id(self, legacy_item: dict, id_or_index):
        return self.get_mapped_value(
            "Location",
            legacy_item,
            self.location_keys,
            self.location_map,
            self.default_location_id,
            "folio_code",
            id_or_index
        )

    def get_mapped_value(
            self, name_of_mapping, legacy_item, legacy_keys, map, default_value, map_key, index_or_id
    ):
        # Gets mapped value from mapping file, translated to the right FOLIO UUID
        field_values = [self.get_value_from_prop_code(legacy_item, k) for k in legacy_keys]
        try:
            right_mapping = next(
                mapping
                for mapping in map
                if all(
                    self.get_value_from_prop_code(legacy_item, k).strip().casefold() in mapping[k].casefold()
                    for k in legacy_keys
                )
            )
            self.add_to_migration_report(
                f"{name_of_mapping} mapping",
                f'{" - ".join(field_values)} -> {right_mapping[map_key]}',
            )
            return right_mapping["folio_id"]
        except StopIteration:
            self.add_to_migration_report(
                f"{name_of_mapping} mapping",
                f'{" - ".join(field_values)} -> {default_value} (Unmapped)',
            )
            return default_value

    @staticmethod
    def get_value_from_prop_code(sierra_item, code: str):
        try:
            if code.startswith("fixedFields"):
                fixed_fields_code = code.split('.')[-1]
                return sierra_item.get("fixedFields", {}).get(fixed_fields_code, {}).get("value")
            elif code.startswith("varFields"):
                raise TransformationCodeError(sierra_item["id"], "varFields not setup in value_from_pro", code)
            elif "." in code:
                temp_prop = sierra_item
                path = code.split(".")

                last = path[-1]
                for p in path:
                    if p != last:
                        temp_prop = temp_prop.get(p, {})
                    else:

                        return temp_prop.get(p)
            elif "." not in code:
                return str(sierra_item.get(code))
            raise TransformationProcessError(sierra_item["id"], "Property code type not mapped", code)
        except Exception as exception:
            raise TransformationCriticalDataError(sierra_item["id"], "Property not found in item", code)


def dedupe(list_of_dicts):
    # TODO: Move to interface or parent class
    return [dict(t) for t in {tuple(d.items()) for d in list_of_dicts}]


def get_varfield(sierra_item, field_tag, tag, strict=False):
    try:
        var_fields_i = next(
            (vf for vf in sierra_item["varFields"] if field_tag in vf["fieldTag"]), {}
        )
        if "subfields" in var_fields_i:
            return next(
                (
                    sf["content"]
                    for sf in var_fields_i["subfields"]
                    if sf.get("tag") == tag
                ),
                "",
            )
        elif strict is False:
            return var_fields_i.get("content", "")
        else:
            return ""
    except Exception as ee:
        print(ee)
        print(sierra_item)
        raise ee


def get_varfields_no_subfield(sierra_item, field_tag):
    try:
        return (
            vf.get("content", "")
            for vf in sierra_item["varFields"]
            if field_tag in vf["fieldTag"]
        )
    except Exception as ee:
        print(ee)
        print(sierra_item)
        raise ee
