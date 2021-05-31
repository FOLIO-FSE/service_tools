import csv
import pandas
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
        super().__init__()
        self.millennium_items_path = args.data_path
        self.result_file = os.path.join(args.result_path, "millennium_sierra_items.json")
        self.csv_result_file = os.path.join(args.result_path, "csv_results.csv")
        self.sierra_items = {}

    def do_work(self):
        print("Let's get started!")
        written = 0
        unequal = 0
        unequal_rows = []
        dict_list = []

        with open(self.millennium_items_path, "r") as millennium_items_file, open(self.result_file,'w+') as results_file, open(self.csv_result_file, "w") as csv_result_file:
            # Loop through all the rows
            for row_index, row in enumerate(millennium_items_file):
                # Remove trailing and leading quotes
                row = row[1:-2]

                # The first row contains the hearders from the first row
                if row_index == 0:
                    headers = row.split('","')
                    # Delete duplicate columns based on header name
                    duplicate_columns = list_duplicates(headers)
                    for column in sorted(duplicate_columns, reverse=True):
                        del headers[column]

                # The remaining rows each represent an item
                else:
                    # Remove trailing and leading quotes
                    item = row.split('","')

                    # Find the index of the first occuring item ID
                    item_id_index = [i for i, item in enumerate(item) if re.search('i[0-9]{7}[0-9x]', item)][0]

                    # Put the bib IDs that occur before the item_id_index in a list 
                    bib_ids = item[:item_id_index]
                    del item[:item_id_index]
                    item.insert(0, bib_ids)

                    # Put the bib class numbers that occur after the item_id_index into another list 
                    bib_call_nos = item[3:3 + len(bib_ids)]
                    del item[3:3 + len(bib_ids)]
                    item.insert(3, bib_call_nos)
                    
                    # Delete duplicate columns based on header name
                    for column in sorted(duplicate_columns, reverse=True):
                        del item[column]
                    
                    # Report any unexpected columns
                    if len(headers) != len(item):
                        unequal += 1
                        unequal_rows.append(item[1])

                    # Create a dictionary with the headers as keys and item columns as values
                    item_as_dict = dict(zip(headers, item))

                    # Translate the item dictionary into a Sierra style item object
                    sierra_object = self.dict_to_sierra_structure(item_as_dict)
                    # print(json.dumps(sierra_obj, indent=4))
                    
                    # Remove fields with "" and " " values
                    elements_to_remove = []
                    for element in sierra_object["fixedFields"]:
                        if sierra_object["fixedFields"][element]["value"] == "" or sierra_object["fixedFields"][element]["value"] == " ":
                            elements_to_remove.append(element)          
                    for element in elements_to_remove:
                        del sierra_object["fixedFields"][element]

                    results_file.write(f"{json.dumps(sierra_object, ensure_ascii=False)}\n")
                    dict_list.append(item_as_dict)

                
                    written += 1
                     # Report progress
                    if written % 5000 == 0:
                        print(f"{written} records created!", flush=True)
                
                # millennium_items_file[row_index] = row
                # print(millennium_items_file)

            items_df = pandas.DataFrame(dict_list)
            items_df.to_csv(csv_result_file, quoting=csv.QUOTE_ALL, index=False, line_terminator='\n')

            print(f"Done!\nNumber of rows processed: {row_index}\nNumber of Sierra-like records created: {written}\nA total of {unequal} rows had unexpected column counts:\n {unequal_rows}")

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
            "bwCallNumbers": millennium_dict.get("CLASS NO.(BIBLIO)", ""),
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
                                     "data_path", "Path to the delimited file. Note that the script is tailored to handle a specific sequence of trailing characters.", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Folder where results will be saved", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="Path to the delimited file. Note that the script is tailored to handle a specific sequence of trailing characters.")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="Folder where results will be saved")


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [idx for idx, item in enumerate(seq) if item in seen or seen_add(item)]