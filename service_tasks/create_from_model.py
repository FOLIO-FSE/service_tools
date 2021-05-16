import csv
import json
import uuid
import re

from service_tasks.service_task_base import ServiceTaskBase
import traceback


class CreateRecordFromModel(ServiceTaskBase):
# Open file and read into a Pandas Dataframe
    def __init__(self, args):
        print("\n~*~*~\nLet's get started!")
        self.data_file = args.data_file
        self.result_file = args.save_to_folder + "/modelled_records.json"
        self.model_file = args.model_record
        self.dedupe = args.dedupe
        self.map_out = args.save_to_folder + "/id_map.json"


    def do_work(self):
        with open(self.data_file) as data_file, open(self.model_file) as model_file:
            # Create a list to store created records in
            records = []
            rows_processed = 0
            unique_processed = []
            id_map = {}
            
            # Open the model and identify the values that should be replaced with data
            model = str(json.load(model_file))
            fields_to_replace = re.findall("\{\{[a-zA-Z0-9_]*\}\}", model)
            print(f"Field tokens to replace with data: {fields_to_replace}")

            # Read the data into a data frame
            # data = pd.read_csv(data_file)
            data = csv.DictReader(data_file)

            for row in data:
                try:
                    rows_processed += 1
                    if rows_processed % 100 == 0:
                        print(rows_processed)
                    # Create a new record based on the model
                    if row[self.dedupe] not in unique_processed:
                        record = model
                        

                        # Loop through the fields, and replace with values from the data
                        for field in fields_to_replace:
                            name = field[2:-2]
                            if name.startswith("new_uuid"):
                                this_uuid = str(uuid.uuid4())
                                record = record.replace(field, this_uuid)
                                id_map[row[self.dedupe]] = {name : this_uuid}
                            elif row[name]:
                                record = record.replace(field, str(row[name]))
                        try:
                            # Add record to list and list of processed records
                            record = eval(record)
                            records.append(record)
                        except SyntaxError as se:
                            print("\nError. Double check record:", se, record)
                        unique_processed.append(row[self.dedupe])
                except KeyError as e:
                    print(f"Make sure that this field is in your headers AND model record: {e}")
                    raise
            
                
            with open(self.result_file, "w") as results_out, open(self.map_out, "w") as map_out:
                print(json.dumps(records, ensure_ascii=False), file=results_out)
                print(id_map, file=map_out)


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