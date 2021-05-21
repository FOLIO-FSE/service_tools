import ast
import csv
import os
import re
from abc import abstractmethod

from service_tasks.service_task_base import ServiceTaskBase


class VirtualBoundWithItemHandler(ServiceTaskBase):
    def __init__(self, args):
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
            for row_index, row in enumerate(reader):
                # If location == none, we are dealing with a "Virtual bound-with"
                if row["I LOCATION"].strip() == "none":
                    b = ast.literal_eval(row["RECORD #(BIBLIO)"])[0]
                    # TODO: Report if more b-numbers
                    # Create tuple of bib number and class mark
                    if b in self.virtual_bound_withs:
                        self.virtual_bound_withs[b].append((b, row["CLASS NO.(ITEM)"]))
                    else:
                        self.virtual_bound_withs[b] = [(b, row["CLASS NO.(ITEM)"])]
                    # Since we are not carrying these fields over, just spit them out and count them
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
                f"Done!\nNumber of rows processed: {row_index}\nA total of {len(self.virtual_bound_withs)} "
                f"were artificial items {with_v}-{with_donor}-{with_note} ")
            source_file.seek(0)
            reader.__init__(source_file)
            unmatched = 0
            for row_index2, row2 in enumerate(reader):
                if row2["I LOCATION"].strip() != "none":
                    bib_ids = ast.literal_eval(row2["RECORD #(BIBLIO)"])
                    bib_class_numbers = ast.literal_eval(row2["CLASS NO.(BIBLIO)"])
                    item_class_number = row2["CLASS NO.(ITEM)"]
                    if len(bib_ids) > 1 and not item_class_number.strip():
                        reg = r'\[[0-9]{0,3}\]?-?(\s(and|\&)\s)?\[?[0-9]{0,3}-?[0-9]{0,3}\](\/S)?'
                        b_1 = re.sub(reg, "", bib_class_numbers[0])
                        if not item_class_number.strip() and all(
                                bc.strip() and bc.startswith(b_1) for bc in bib_class_numbers):
                            row2["CLASS NO.(ITEM)"] = b_1
                        else:
                            unmatched += 1
                            print(f"{unmatched} bound-with without Item class mark or inconsistent classmarks:\t{row2['RECORD #(ITEM)']} -- {bib_class_numbers}")
                    else:
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
                        row2["CLASS NO.(BIBLIO)"] = str(bib_class_numbers)
                    if row2["CLASS NO.(BIBLIO)"] == "['']":
                        row2["CLASS NO.(BIBLIO)"] = ""
                    writer.writerow(row2)
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
