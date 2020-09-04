import json
import uuid
from abc import abstractmethod
from pymarc import MARCReader
import os.path
from service_tasks.service_task_base import ServiceTaskBase, print_dict_to_md_table


class ExtractItemInfoFromMARC(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.source_file_path = args.source_path
        self.results_file_path = args.results_path
        self.holdings = {}
        self.items = []
        with open(args.instance_id_map_path, "r") as map_file:
            self.instance_id_map = json.load(map_file)

    def do_work(self):
        with open(self.source_file_path, "rb") as marc_file, open(os.path.join(self.results_file_path, "items.json"),
                                                                  "w+") as items_file, open(
            os.path.join(self.results_file_path, "holdings.json"), "w+") as holdings_file:
            reader = MARCReader(marc_file, "rb", permissive=True)
            for record in reader:
                legacy_id = record['035']['a']
                for f999 in record.get_fields("999"):
                    self.add_stats("999")
                    holding = {"id": str(uuid.uuid4()),
                               "instanceId": self.instance_id_map[legacy_id]['id'],
                               "metadata": self.folio_client.get_metadata_construct(),
                               "permanentLocationId": "b982e488-306f-4caf-a14e-4e5ed78e8fef",
                               "callNumber": f999["a"]
                               }
                    if f999["w"] == "DEWEY":
                        holding["callNumberTypeId"] = "03dd64d0-5626-4ecd-8ece-4531e0069f35"
                    elif f999["w"] == "ALPHANUM":
                        holding["callNumberTypeId"] = "6caca63e-5651-4db6-9247-3205156e9699"

                    else:
                        raise Exception(f"Classification type {f999['w']} not handled")

                    item = {"id": str(uuid.uuid4()),
                            "holdingsRecordId": holding["id"],
                            "barcode": f999["i"],
                            "permanentLoanTypeId": "2b94c631-fca9-4892-a730-03ee529ffe27",
                            "status": {"name": "Available"},
                            "copyNumber": f999["c"],
                            "notes": [],
                            "metadata": self.folio_client.get_metadata_construct()
                            }

                    if f999["t"] == "TESIS":
                        item["materialTypeId"] = "d9acad2f-2aac-4b48-9097-e6ab85906b25"
                    elif f999["t"] == "TESIS_CD":
                        item["materialTypeId"] = "dd0bf600-dbd9-44ab-9ff2-e2a61a6539f1"
                    elif f999["t"] == "LIBRO":
                        item["materialTypeId"] = "1a54b431-2e4f-452d-9cae-9cee66c9a892"
                    else:
                        raise Exception(f"unhandled material type:{f999['t']}")

                    if "z" in f999:
                        item["notes"].append({"itemNoteTypeId": "695e029d-045f-406d-8597-5f475fb150d1",
                                              "note": f999["z"], "staffOnly": True})
                    if "g" in f999:
                        item["notes"].append({"itemNoteTypeId": "49d037c1-9df8-41da-945e-a2b1778bfd0d",
                                              "note": f999["g"], "staffOnly": True})

                    if "x" in f999:
                        item["notes"].append({"itemNoteTypeId": "d25fc2cb-0337-4f45-8332-f3088b909df5",
                                              "note": f999["x"], "staffOnly": True})
                    if "u" in f999:
                        item["notes"].append({"itemNoteTypeId": "7e85a68a-423b-4525-8789-ef60cb43d9c5",
                                              "note": f999["u"], "staffOnly": True})

                    if "n" in f999:
                        item["notes"].append({"itemNoteTypeId": "52b284bc-e2af-4fd4-8b7a-68ac3555dbd2",
                                              "note": f999["n"], "staffOnly": True})

                    for i, k in zip(f999.subfields[0::2], f999.subfields[1::2]):
                        self.add_stats(i)

                    holdings_key = self.to_key(holding)
                    existing_holding = self.holdings.get(holdings_key, None)
                    if not existing_holding:
                        self.holdings[holdings_key] = holding
                        self.add_stats("holdings")
                    else:
                        print(f"{item['id']} - {existing_holding['id']}")
                        item["holdingsRecordId"] = existing_holding["id"]

                    self.items.append(item)
                    self.add_stats("items")
            print_dict_to_md_table(self.stats)
            for i in self.items:
                self.write_object(i, items_file)
            for h in self.holdings.values():
                self.write_object(h, holdings_file)

    def write_object(self, obj, file):
        # TODO: Move to interface or parent class
        file.write("{}\n".format(json.dumps(obj)))

    def to_key(self, holding):
        """creates a key if key values in holding record
        to determine uniquenes"""
        # TODO: Move to interface or parent class
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
    @abstractmethod
    def add_arguments(sub_parser):
        sub_parser.add_argument("source_path", widget="FileChooser")
        sub_parser.add_argument("results_path", widget="DirChooser")
        sub_parser.add_argument("instance_id_map_path", widget="FileChooser")
