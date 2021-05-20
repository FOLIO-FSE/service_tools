import csv
import json
import uuid
import re
import urllib.parse

from service_tasks.service_task_base import ServiceTaskBase

class CreateRecordFromModel(ServiceTaskBase):
    # Open file and read into a Pandas Dataframe
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("\n~*~*~\nLet's get started!")
        self.data_file = args.data_file
        self.model_file = args.model_record
        self.record_type = args.record_type
        self.map_key = args.map_key
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
            fetched_uuids = 0
            generated_uuids = 0
            mapped_uuids = 0

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

            # For each row, create a new record based on the model
            for row in data:
                record = model

                try:
                    # Loop through the fields, and replace with values from the data
                    for field in fields_to_replace:
                        field_name = field[2:-2]
                        if field_name.startswith("new_uuid"):
                            new_uuid = str(uuid.uuid4())
                            record = record.replace(field, new_uuid)
                            generated_uuids += 1
                            id_map[row[self.map_key]][self.record_type] = new_uuid
                        elif field_name.startswith("mapped_uuid"):
                            try:
                                mapped_id = row[self.map_key]
                                content = id_map[mapped_id][field_name[12:]]
                                record = record.replace(field, content)
                                mapped_uuids += 1
                            except KeyError as ke:
                                print(f"Missing key in ID map: {ke}")
                        elif field_name.startswith("fetch_uuid"):
                            linked_uuid = self.fetch_linked_rec_uuid(field_name, row)
                            if linked_uuid:
                                record = record.replace(field, linked_uuid)
                                id_map[row[self.map_key]]["license"] = linked_uuid
                                fetched_uuids += 1
                            else:
                                record = record.replace(field, "")
                        elif row[field_name] != "":
                            content = row[field_name].replace("'", "\\'")
                            record = record.replace(field, content)
                        else:
                            record = record.replace(field, "")
                            if field_name not in empty_fields:
                                empty_fields[field_name] = 1
                            else:
                                empty_fields[field_name] += 1

                    # Add record to list and list of processed records. Print parsing error and move on.
                    try:
                        record = eval(record)
                    except SyntaxError as se:
                        print("\nError. Double check record:", se, record)

                    # Do a little danse to rempve empty customProperties from licenses
                    if self.record_type == "license":
                        self.remove_empty_license_terms(record)

                    # Append record to list
                    records.append(record)
                    unique_processed.append(row[self.map_key])

                except KeyError as e:
                    print(
                        f"Make sure that this field is in your headers AND model record: {e}")
                    raise

                rows_processed += 1
                if rows_processed % 50 == 0:
                    print(f"{rows_processed} rows processed")
                elif rows_processed == 1:
                    print(record)

            with open(self.result_file, "w") as results_out, open(self.map_file, "w") as map_out:
                print(json.dumps(records, ensure_ascii=False), file=results_out)
                print(json.dumps(id_map), file=map_out)

            print(f"Number of records processed: {rows_processed}")
            print(f"Number of records created: {len(records)}")
            print(f"Number of empty fields: {empty_fields}")
            print(
                f"Number of empty custom properties removed: {cust_props_removed}")
            print(*records[:2], sep="\n")
            print(f"Number of UUIDs generated: {generated_uuids}")
            print(f"Number of UUIDs added from map: {mapped_uuids}")
            print(f"Number of UUIDs added from FOLIO: {fetched_uuids}")




    def remove_empty_license_terms(record):
        ''' Remove empty fields from license terms. If the license term does not have a value, remove tge term itself.'''
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

    def fetch_linked_rec_uuid(self, field_name, row):
        '''Get the id of a records that matches a certain criterium. Useful if you are linking to something alredy in FOLIO and don't have the ID.'''
        match_value = row[field_name[11:]]
        query = "?filters=" + \
            urllib.parse.quote("name==" + match_value)
        if self.record_type == "agreement":
            matching_license = self.folio_client.folio_get(
                "/licenses/licenses", query=query)
            if len(matching_license) == 1:
                linked_uuid = matching_license[0]["id"]
                return linked_uuid
            else:
                print(f"Too few/many items for {row[match_value]}!")
        else:
            print(
                f"Fetch linked UUID not built for {self.record_type}. Check map against code.")

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_argument(sub_parser,
                                     "data_file",
                                     "A csv file containing one object per row.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "model_record",
                                     "A valid FOLIO json object, with mapped fields -- corresponding to the data column headers -- enclosed in {{}}.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "record_type",
                                     "Name of the record type. Will be used in result file name and to qualify the UUID in the output ID map.",
                                     ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "id_map",
                                     "OPTIONAL An ID map. If left blank, one will be created.",
                                     "FileChooser", required=False),
        ServiceTaskBase.add_argument(sub_parser,
                                     "map_key",
                                     "Will be used as a unique key in the (provided or generated) id_map.", ""
                                     )

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "data_file",
                                         "the csv or tsv file to be analyzed. If csv, all rows must have the same number of columns"),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "model_record",
                                         "A json record with desired objects and mapped fields."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "save_to_folder",
                                         "Folder where you want the output to be saved."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "record_type",
                                         "Name of the record type. Will be used in result file name and to qualify the UUID in the output ID map."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "id_map",
                                         "An existing ID map. If left blank, one will be created."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "map_key",
                                         "Will be used as a unique key in the (provided or generated) id_map.")