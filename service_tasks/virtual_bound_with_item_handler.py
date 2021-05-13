import ast
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


class VirtualBoundWithItemHandler(ServiceTaskBase):
    def __init__(self, args):
        self.source_path = args.data_path
        self.result_file = os.path.join(args.result_path, "restructured_virtual_bound_with_items.tsv")
        self.bibs_and_class = {}

    def do_work(self):
        print("Let's get started!")
        written = 0
        unequal = 0
        unequal_rows = []
        dict_list = []
        located_real_items = 0
        virtual_real_matches = 0
        with_v = 0
        with_donor = 0
        with_note = 0

        with open(self.source_path, "r") as source_file, open(self.result_file, 'w+') as results_file:
            # Loop through all the rows
            reader = csv.DictReader(source_file)
            writer = csv.DictWriter(results_file, fieldnames=reader.fieldnames, delimiter='\t', lineterminator="\n")
            writer.writeheader()
            for row_index, row in enumerate(reader):
                if row["I LOCATION"].strip() == "none":
                    b = ast.literal_eval(row["RECORD #(BIBLIO)"])[0]
                    # TODO: Report if more b-numbers
                    self.bibs_and_class[b] = row["CLASS NO.(ITEM)"]
                    if row["VOLUME"].strip():
                        print(f'Volume:\t {row["RECORD #(ITEM)"]}\t{row["VOLUME"]}')
                        with_v += 1
                    if row["DONOR"].strip():
                        print(f'Donor:\t {row["RECORD #(ITEM)"]}\t{row["DONOR"]}')
                        with_donor += 1
                    if row["NOTE(ITEM)"].strip():
                        print(f'Note:\t {row["RECORD #(ITEM)"]}\t{row["NOTE(ITEM)"]}')
                        with_note += 1
            print(
                f"Done!\nNumber of rows processed: {row_index}\nA total of {len(self.bibs_and_class)} were artificial items {with_v}-{with_donor}-{with_note} ")
            source_file.seek(0)
            reader.__init__(source_file)
            for row_index2, row2 in enumerate(reader):
                if row2["I LOCATION"].strip() != "none":
                    bs = ast.literal_eval(row2["RECORD #(BIBLIO)"])
                    bib_class_numbers = ast.literal_eval(row2["CLASS NO.(BIBLIO)"])
                    for i, b in enumerate(bs):
                        if b in self.bibs_and_class:
                            if i == 1:
                                located_real_items += 1
                            virtual_real_matches += 1
                            index_of_b = bs.index(b)
                            bib_class_numbers[index_of_b] = self.bibs_and_class[b]
                    row2["CLASS NO.(BIBLIO)"] = str(bib_class_numbers)
                else:
                    if row["RECORD #(BIBLIO)"] == "['']":
                        row["RECORD #(BIBLIO)"] = ""
                    if row["CLASS NO.(BIBLIO)"] == "['']":
                        row["CLASS NO.(BIBLIO)"] = ""
                writer.writerow(row2)
            print(f"{located_real_items}! {virtual_real_matches}")



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
