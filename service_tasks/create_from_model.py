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
        self.model_file = args.model_record
        self.record_type = args.record_type
        self.matchpoint = args.matchpoint
        self.result_file = f"{args.save_to_folder}/{self.record_type}.json"
        self.map_file = args.id_map

    def do_work(self):
        with open(self.data_file) as data_file, open(self.model_file) as model_file:
            # Create a list to store created records in
            records = []
            rows_processed = 0
            unique_processed = []
            empty_fields = {}
            cust_props_removed = 0


            if self.map_file != "none":
                with open(self.map_file) as map_in:
                    id_map = json.load(map_in)
            else:
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
                    if row[self.matchpoint] not in unique_processed:
                        record = model
                        

                        # Loop through the fields, and replace with values from the data
                        for field in fields_to_replace:
                            field_name = field[2:-2]
                            if field_name.startswith("new_uuid"):
                                this_uuid = str(uuid.uuid4())
                                record = record.replace(field, this_uuid)
                                id_map[row[self.matchpoint]] = {self.record_type : this_uuid}
                            elif field_name.startswith("mapped_uuid"):
                                id_match = row[self.matchpoint]
                                id_map.get(field_name[12:])
                                content = id_map[id_match].get(field_name[12:])
                                record = record.replace(field, content)
                            elif row[field_name] != "":
                                content = row[field_name].replace("'","\\'")
                                record = record.replace(field, content)
                            else:
                                record = record.replace(field, "")
                                if field_name not in empty_fields:
                                    empty_fields[field_name] = 1
                                else:
                                    empty_fields[field_name] += 1

                        try:
                            # Add record to list and list of processed records
                            record = eval(record)

                            # Do a little danse to rempve empty customProperties from licenses
                            if self.record_type == "license":
                                if record["customProperties"]:
                                    props = record["customProperties"]
                                    for prop in props:
                                        if props[prop][0].get("note") == "":
                                            del props[prop][0]["note"]
                                            cust_props_removed += 1
                                        if props[prop][0].get("value") == "":
                                            del props[prop][0]["value"]
                                            cust_props_removed += 1

                                    clean_props = {k: v for k, v in props.items() if any(v)}
                                    record["customProperties"] = clean_props
                                    

                                            
                             # Append record to list               
                            records.append(record)

                        except SyntaxError as se:
                            print("\nError. Double check record:", se, record)
                        unique_processed.append(row[self.matchpoint])
                except KeyError as e:
                    print(f"Make sure that this field is in your headers AND model record: {e}")
                    raise
            
                
            with open(self.result_file, "w") as results_out, open(self.map_file, "w") as map_out:
                print(json.dumps(records, ensure_ascii=False), file=results_out)
                print(json.dumps(id_map), file=map_out)


            print(f"Number of records processed: {rows_processed}")
            print(f"Number of records created: {len(records)}")
            print(f"Number of empty fields: {empty_fields}")
            print(f"Number of empty custom properties removed: {cust_props_removed}")


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
                                     "id_map",
                                     "An ID map (as created by this script).",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "record_type",
                                     "Name of the record type. Will be used in result file name and to qualify the UUID in the output ID map..",
                                     "")
        ServiceTaskBase.add_argument(sub_parser,
                                     "matchpoint",
                                     "Select a field that will be used to dedupe the rows (using the first occurence). If unique, no deduping will occur.", ""
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
                                     "id_map",
                                     "An ID map (as created by this script)."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "record_type",
                                     "Name of the record type. Will be used in result file name and to qualify the UUID in the output ID map."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "matchpoint",
                                     "Select a field that will be used to dedupe the rows (using the first occurence). If unique, no deduping will occur..",
                                    )                                