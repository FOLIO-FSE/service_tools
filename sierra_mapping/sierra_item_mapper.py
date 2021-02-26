import json
import uuid
from typing import re

from folioclient import FolioClient

from user_migration.mappers.mapper_base import MapperBase


class SierraItemTransformer(MapperBase):
    def __init__(self, folio_client: FolioClient, instance_id_map, loan_type_map, material_type_map, location_map):
        super().__init__(folio_client)
        self.holdings = {}
        self.stats = {}
        self.loan_type_map = loan_type_map
        self.material_type_map = material_type_map
        self.location_map = location_map
        self.item_id_map = {}
        self.circ_note_map = {}
        self.instance_id_map = instance_id_map

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
            # 'enumeration': '',
            # 'chronology': '',
            # yearCaption[]
            "formerIds": [get_varfield(sierra_item, "i", "a")],
            # copyNumbers
            # 'numberOfPieces': '',
            # descriptionOfPieces
            # numberOfMissingPieces
            # missingPieces
            # missingPiecesDate
            # itemDamagedStatusId
            # itemDamagedStatusDate
            "notes": list(self.get_notes(sierra_item)),
            # "circulationNotes": list(self.get_circ_notes(sierra_item)),
            "status": self.get_status(sierra_item),
            "materialTypeId": self.get_material_type_id(sierra_item),
            "permanentLoanTypeId": self.get_loan_type_id(sierra_item),
            "metadata": self.folio_client.get_metadata_construct(),
            # temporaryLoanTypeId
            # permanentLocationId
            # temporaryLocationId
            # electronicAccess
            # statisticalCodeIds
            # purchaseOrderLineIdentifier
            # tags
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
        if not new_item["volume"]:
            del new_item["volume"]
        return new_item

    def convert_to_holding(self, sierra_item):
        if len(sierra_item["bibIds"]) > 1:
            self.add_stats(self.stats, "Item connected to more than one Bib/Instance")
        sierra_bib_id = next(f[0] for f in sierra_item["bibIds"])
        if ',' in sierra_bib_id:
            sierra_bib_id = sierra_bib_id.split(',')[0]
        sierra_bib_id = re.sub(r"^\.b|b", "", sierra_bib_id)
        # print(sierra_bib_id)
        new_instance_id = self.instance_id_map.get(sierra_bib_id, {}).get("folio_id", "")

        if not new_instance_id:
            self.add_stats(self.stats, f"Bib Id not in list of migrated records")
            self.add_to_migration_report(
                "Sierra Items without migrated Instances. Must be corrected",
                f"Sierra Bib Id {sierra_bib_id} missing in migrated bibs for Sierra Item {sierra_item['id']}",
            )
            print(f"{sierra_bib_id} {next(iter(self.instance_id_map.items()))}")
            raise ValueError(
                f'Missing Instances in map - Sierra Item {sierra_item["id"]} with bibIds:{sierra_item["bibIds"]}'
            )
        else:
            self.add_stats(self.stats, f"Mapped instance ids")

        new_holding = {
            "id": str(uuid.uuid4()),
            # holdingsTypeId
            "formerIds": list(),
            "instanceId": new_instance_id,
            "permanentLocationId": self.get_location(sierra_item),
            "callNumberTypeId": "6caca63e-5651-4db6-9247-3205156e9699",
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

    def get_material_type_id(self, sierra_item):
        try:
            code = sierra_item.get("fixedFields", {}).get("61", {}).get("value", "").strip()
            folio_id = self.material_type_map.get(code, self.material_type_map.get('*', ''))
            self.add_to_migration_report("Material type mapping", f"{code} -> {folio_id} ", )
            return folio_id
        except Exception:
            self.add_to_migration_report(
                "Material type mapping - Unsuccessful",
                f"Sierra i type code {code} not mapped",
            )
            raise ValueError(f"Sierra i type code {code} not mapped to material type")

    def get_loan_type_id(self, sierra_item):
        try:
            code = sierra_item.get("fixedFields", {}).get("61", {}).get("value", "").strip()
            folio_id = self.loan_type_map.get(code, self.loan_type_map.get('*', ''))
            self.add_to_migration_report("Loan type mapping", f"{code} -> {folio_id} ", )
            return folio_id
        except Exception:
            self.add_to_migration_report(
                "Loan type mapping - Unsuccessful",
                f"Sierra i type code {code} not mapped",
            )
            raise ValueError(f"Sierra i type code {code} not mapped to Loan type")

    @staticmethod
    def add_stats(stats, measure_to_add):
        if measure_to_add not in stats:
            stats[measure_to_add] = 1
        else:
            stats[measure_to_add] += 1

    def get_location(self, sierra_item):
        try:
            iii_loc = sierra_item.get("location", {}).get("code", "")
            self.add_to_migration_report("Sierra Locations", f"{iii_loc}")
            if len(self.location_map) == 1:
                self.add_to_migration_report("Folio Locations", f"{self.location_map['*']}")
                return self.location_map['*']
            else:
                folio_loc = self.location_map.get(iii_loc, "")
                if folio_loc:
                    self.add_to_migration_report("Folio Locations", f"{folio_loc}")
                    return folio_loc
                else:
                    self.add_to_migration_report("ACTION ITEM: Sierra locations not found in map", f"{iii_loc}")
                    return self.location_map['*']
        except Exception as ee:
            print(sierra_item)
            raise ee

    def get_circ_notes(self, sierra_item):
        source = {
            "id": self.folio_client.current_user,
            "personal": {"lastName": "Sierra", "firstName": "Migrated"},
        }
        for note_m in get_varfields_no_subfield(sierra_item, "m"):
            if note_m:
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
