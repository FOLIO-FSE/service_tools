import csv
import pandas
import json
import os
import re
from abc import abstractmethod
from os import listdir
from os.path import isfile, join
from datetime import datetime as dt, timedelta

from helpers.custom_dict import InsensitiveDictReader
from service_tasks.service_task_base import ServiceTaskBase

class ParseIIICsvItemsWithBoundiwths(ServiceTaskBase):
    def __init__(self, args):
        csv.register_dialect("tsv", delimiter="\t")
        super().__init__()
        self.millennium_items_path = args.data_path
        self.result_file = os.path.join(args.result_path, "items_with_boundwiths_handled.csv")
        self.sierra_items = {}

    def do_work(self):
        print("Let's get started!")
        written = 0
        unequal = 0
        unequal_rows = []
        dict_list = []

        with open(self.millennium_items_path, "r",encoding='utf-8') as millennium_items_file:
            if self.millennium_items_path.endswith("tsv"):
                reader = InsensitiveDictReader(millennium_items_file, dialect="tsv")
            else:
                reader = InsensitiveDictReader(millennium_items_file)
            # Loop through all the row
            try:
                for row_index, item_dict in enumerate(reader):
                    # The first row contains the headers from the first row
                    # TODO: Why are we looking for duplicate columns?
                    '''if row_index == 0:
                        headers = row.split('","')
                        # Delete duplicate columns based on header name
                        duplicate_columns = list_duplicates(headers)
                        for column in sorted(duplicate_columns, reverse=True):
                            del headers[column]'''

                    # The remaining rows each represent an item

                    # Remove trailing and leading quotes
                    item = list(item_dict.values())

                    # Find the index of the first occurring item ID
                    item_id_index = [i for i, item in enumerate(item) if re.search('i[0-9]{7}[0-9x]', item)][0]

                    # Put the bib IDs that occur before the item_id_index in a list
                    bib_ids = item[:item_id_index]
                    del item[:item_id_index]
                    item.insert(0, bib_ids)

                    # Put the bib class numbers that occur after the item_id_index into another list
                    bib_call_nos = item[3:3 + len(bib_ids)]
                    del item[3:3 + len(bib_ids)]
                    item.insert(3, bib_call_nos)

                    # Create a dictionary with the headers as keys and item columns as values
                    item_as_dict = dict(zip(item_dict.keys(), item))

                    dict_list.append(item_as_dict)

                    written += 1
                    # Report progress
                    if written % 5000 == 0:
                        print(f"{written} records created!", flush=True)
            except Exception as ee:
                print(row_index)
                raise(ee)

            items_df = pandas.DataFrame(dict_list)
            items_df.to_csv(self.result_file, quoting=csv.QUOTE_ALL, index=False, line_terminator='\n')

            print(f"Done!\nNumber of rows processed: {row_index}\nA total of {unequal} rows had unexpected column counts:\n {unequal_rows}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "data_path", "Path to the delimited file.", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Folder where results will be saved", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="Path to the delimited file.")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="Folder where results will be saved")


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [idx for idx, item in enumerate(seq) if item in seen or seen_add(item)]