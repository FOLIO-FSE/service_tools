import ast
import csv
import os
import re
from abc import abstractmethod

from service_tasks.service_task_base import ServiceTaskBase


class GVSUVirtualBoundWithItemHandler(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.source_path = args.data_path
        self.result_file = os.path.join(args.result_path, "restructured_virtual_bound_with_items.tsv")
        self.virtual_bound_withs = {}
        self.perfect_bound_with = []

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
            unmatched = 0
            for row_index, row in enumerate(reader):
                if row["location"].strip() != "none":
                    bib_ids = ast.literal_eval(row["record number(bibliographic)"])
                    bib_class_numbers = ast.literal_eval(row["call no.bib"])
                    item_class_number = row["call no."]

                    for i, b in enumerate(bib_ids):
                        vb_tuples = self.virtual_bound_withs.get(b, [])
                        # pull up the right virtual bw:
                        virtual_bound_with = next((bc_tuple for bc_tuple in vb_tuples if
                                                   bc_tuple[0] == b and bc_tuple[1].startswith(item_class_number)),
                                                  None)

                        if virtual_bound_with:
                            located_real_items += 1
                            virtual_real_matches += 1
                            index_of_b = bib_ids.index(b)
                            bib_class_numbers[index_of_b] = virtual_bound_with[1]
                    row["CLASS NO.(BIBLIO)"] = str(bib_class_numbers)
                if row["CLASS NO.(BIBLIO)"] == "['']":
                    row["CLASS NO.(BIBLIO)"] = ""
                writer.writerow(row)
            print(f"Located Real Items: {located_real_items}! Virtual Real matches: {virtual_real_matches}")

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
