import csv
import json
import pandas as pd
import re

from service_tasks.service_task_base import ServiceTaskBase
import traceback


class CreateRecordFromModel(ServiceTaskBase):
# Open file and read into a Pandas Dataframe
    def __init__(self, args):
        print("\n~*~*~\nLet's get started!")
        self.data_file = args.data_file
        self.save_to_folder = args.save_to_folder
        self.model_file = args.model_record
        self.dedupe = args.dedupe


    def do_work(self):
        with open(self.data_file) as data_file, open(self.model_file) as model_file:
            # Create a list to store created records in
            records = []
            rows_processed = 0
            unique_processed = []
            
            # Open the model and identify the values that should be replaced with data
            model = json.load(model_file)
            model = str(model)
            fields_to_replace = re.findall("\{\{[a-zA-Z0-9_]*\}\}", model)

            # Read the data into a data frame
            # data = pd.read_csv(data_file)
            data = csv.DictReader(data_file)

            for row in data:
                try:
                    rows_processed += 1
                    # Create a new record based on the model
                    if row[self.dedupe] not in unique_processed:
                        record = model

                        # Loop through the fields, and replace with values from the data
                        for field in fields_to_replace:
                            record = record.replace(field, row[field])

                        # Add record to list and list of processed records
                        records.append(record)
                        unique_processed.append(row[self.dedupe])
                except KeyError as e:
                    print(f"Make sure that this field is in your headers AND model record: {e}")



            print(f"Number of records processed: {rows_processed}")
            print(f"Number of records created: {len(records)}")
            print(*records[:2], sep = "\n")

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "data_file",
                                     "A csv file containing one object per row.",
                                     "FileChooser")
        ServiceTaskBase.add_argument(sub_parser,
                                     "model_record",
                                     "A json record with desired objects and mapped fields.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "dedupe",
                                     "Select a field that will be used to dedupe the rows (using the first occurence). Leave blank if none.", ""
                                    )

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "data_file",
                                         "the csv or tsv file to be analyzed. If csv, all rows must have the same number of columns")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "model_record",
                                     "A json record with desired objects and mapped fields."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "format",
                                     "Format of the data to analyse."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "dedupe",
                                     "Select a field that will be used to dedupe the rows (using the first occurence). Leave blank if none.",
                                    )                                