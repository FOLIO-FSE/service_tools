import csv
import json
import os
import re
from abc import abstractmethod
from os import listdir
from os.path import isfile, join
from datetime import datetime as dt, timedelta

from service_tasks.service_task_base import ServiceTaskBase


class MillenniumItemsToSierraJson(ServiceTaskBase):
    def __init__(self, args):
        self.millennium_items_path = args.data_path
        self.result_file = os.path.join(args.result_path, "millennium_sierra_items.json")
        self.sierra_items = {}

    def do_work(self):
        unequal = 0
        print("here!")
        written = 0
        with open(self.millennium_items_path, "r") as millennium_items_file, open(self.result_file,
                                                                                  'w+') as results_file:
            duplicate_positions = []
            for row_index, row in enumerate(millennium_items_file):
                # Remove trailing and leading quotes
                if row_index == 0:
                    # row = row + '"'
                    row = row[1:-1] + '"'
                    column_names = row.split('","')
                    duplicate_positions = list_duplicates(column_names)
                    for index in sorted(duplicate_positions, reverse=True):
                        del column_names[index]
                else:
                    row = row[1:-2]
                    columns = row.split('","')
                    index_of_i = [i for i, item in enumerate(columns) if re.search('i[0-9]{7}[0-9x]', item)]
                    b_numbers = columns[:(index_of_i[0])]
                    num_bs = len(b_numbers)
                    i_num = columns[index_of_i[0]]
                    remaining_cols = columns[(index_of_i[0]) + 1:]
                    for n in range(num_bs - 1):
                        if any(remaining_cols):
                            del remaining_cols[0]
                    column_values = [b_numbers, i_num] + remaining_cols
                    for index in sorted(duplicate_positions, reverse=True):
                        del column_values[index]
                    if len(column_values) != len(column_names):
                        print(f"{len(column_names)} {column_names}")
                        print(f"{len(column_values)} {json.dumps(column_values, indent=4)}")
                        print(row)
                        unequal += 1
                        raise Exception("Unequal")
                    else:
                        name_to_value_dict = dict(zip(column_names, column_values))
                        sierra_obj = self.dict_to_sierra_structure(name_to_value_dict)
                        # print(json.dumps(sierra_obj, indent=4))
                        results_file.write(f"{json.dumps(sierra_obj)}\n")
                        written += 1
        print(f"Done! {row_index} {unequal} {written}")

    @staticmethod
    def dict_to_sierra_structure(millennium_dict):
        ret = {
            "id": millennium_dict.get("RECORD #(ITEM)", ""),
            "updatedDate": dt.isoformat(dt.utcnow()),
            "createdDate": dt.isoformat(dt.utcnow()),
            "deleted": False,
            "bibIds": millennium_dict.get("RECORD #(BIBLIO)", ""),
            "location": {
                "code": millennium_dict.get("I LOCATION", ""),
                "name": ""
            },
            "status": {
                "code": millennium_dict.get("STATUS", ""),
                "display": ""
            },
            # TODO: Special case for Trinity. remove class number as barcode for others
            "barcode": millennium_dict.get("BARCODE") if millennium_dict.get("BARCODE", "") else millennium_dict.get(
                "CLASS NO.(ITEM)", ""),
            "callNumber": millennium_dict.get("CLASS NO.(ITEM)", ""),
            "itemType": millennium_dict.get("I TYPE", ""),
            "fixedFields": {
                "57": {
                    "label": "BIB HOLD",
                    "value": "false"
                },
                "58": {
                    "label": "COPY #",
                    "value": millennium_dict.get("COPY #", "")
                },
                "59": {
                    "label": "ICODE1",
                    "value": millennium_dict.get("ICODE1", "")
                },
                "60": {
                    "label": "ICODE2",
                    "value": millennium_dict.get("ICODE2", "")
                },
                "61": {
                    "label": "I TYPE",
                    "value": millennium_dict.get("I TYPE", ""),
                    "display": ""
                },
                "62": {
                    "label": "PRICE",
                    "value": millennium_dict.get("PRICE", "")
                },
                "64": {
                    "label": "OUT LOC",
                    "value": millennium_dict.get("I LOCATION", "")
                },
                "68": {
                    "label": "LCHKIN",
                    "value": ""
                },
                "70": {
                    "label": "IN LOC",
                    "value": millennium_dict.get("I LOCATION", "")
                },
                "74": {
                    "label": "IUSE3",
                    "value": millennium_dict.get("INTL USE ", "")
                },
                "76": {
                    "label": "TOT CHKOUT",
                    "value": millennium_dict.get("TOT CHKOUT", "")
                },
                "77": {
                    "label": "TOT RENEW",
                    "value": millennium_dict.get("TOT RENEW", "")
                },
                "78": {
                    "label": "LOUTDATE",
                    "value": ""
                },
                "79": {
                    "label": "LOCATION",
                    "value": millennium_dict.get("I LOCATION", ""),
                    "display": ""
                },
                "80": {
                    "label": "REC TYPE",
                    "value": "i"
                },
                "81": {
                    "label": "RECORD #",
                    "value": millennium_dict.get("RECORD #(ITEM)", "")
                },
                "83": {
                    "label": "CREATED",
                    "value": dt.isoformat(dt.utcnow())  # millennium_dict.get("CREATED(ITEM)", "")
                },
                "84": {
                    "label": "UPDATED",
                    "value": dt.isoformat(dt.utcnow())  # millennium_dict.get("UPDATED(ITEM)", "")
                },
                "85": {
                    "label": "REVISIONS",
                    "value": millennium_dict.get("REVISIONS(ITEM)", "")
                },
                "86": {
                    "label": "AGENCY",
                    "value": "1",
                    "display": "-"
                },
                "88": {
                    "label": "STATUS",
                    "value": millennium_dict.get("STATUS", ""),
                    "display": ""
                },
                "93": {
                    "label": "INTL USE ",
                    "value": millennium_dict.get("INTL USE ", "")
                },
                "94": {
                    "label": "COPY USE",
                    "value": millennium_dict.get("COPY USE", "")
                },
                "97": {
                    "label": "IMESSAGE",
                    "value": millennium_dict.get("IMESSAGE", "")
                },
                "98": {
                    "label": "PDATE",
                    "value": ""
                },
                "108": {
                    "label": "OPACMSG",
                    "value": millennium_dict.get("OPACMSG", "")
                },
                "109": {
                    "label": "YTDCIRC",
                    "value": millennium_dict.get("YTDCIRC", "")
                },
                "110": {
                    "label": "LYCIRC",
                    "value": "0"
                },
                "127": {
                    "label": "AGENCY",
                    "value": "1",
                    "display": "-"
                },
                "161": {
                    "label": "VI CENTRAL",
                    "value": "0"
                },
                "162": {
                    "label": "IR DIST LEARN SAME SITE",
                    "value": "0"
                },
                "264": {
                    "label": "Holdings Item Tag",
                    "value": "0"
                },
                "265": {
                    "label": "Inherit Location",
                    "value": "false"
                },
                "991": {
                    "label": "donor",
                    "value": millennium_dict.get("DONOR", "")
                }
            },
            "varFields": [
                {
                    "fieldTag": "m",
                    "content": millennium_dict.get("NOTE(ITEM)", "")
                },
                {
                    "fieldTag": "v",
                    "content": millennium_dict.get("VOLUME", "")
                }
            ]
        }
        return ret

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "data_path", "Path to the file", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Path to the file", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="path to millenium file")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="path to results file")


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [idx for idx, item in enumerate(seq) if item in seen or seen_add(item)]
