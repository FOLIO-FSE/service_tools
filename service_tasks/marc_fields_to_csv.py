from abc import abstractmethod
from pymarc import MARCReader
import csv
import pandas
import os.path
from service_tasks.service_task_base import ServiceTaskBase


class MARCFieldsToCSV(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        print("Let's get started!")
        self.source_file_path = args.source_path
        self.save_to_file = args.save_to_file
        self.fields_to_csv = args.fields_to_csv

    def do_work(self):
        with open(self.source_file_path, "rb") as marc_file:
            reader = MARCReader(marc_file, "rb", permissive=True)
            list_of_records = []

            for record in reader:
                record_dict = {}

                fields_to_add = self.fields_to_csv.split(",")
                main_field =  fields_to_add[0]
                other_fields = fields_to_add[1:]

                for main_field in record.get_fields(main_field):
                    record_dict = {}
                    self.get_values(main_field, record_dict)

                    for other_field in other_fields:
                        for field in record.get_fields(other_field):
                            self.get_values(field, record_dict)

                    list_of_records.append(record_dict)

            field_df = pandas.DataFrame(list_of_records)

            print(field_df.head())

            field_df.to_csv(self.save_to_file, index=False, quoting=csv.QUOTE_ALL)


    def get_values(self, field, record_dict):
        if field.tag not in '001':
            for code in list(field.subfields_as_dict().keys()):
                for subfield in field.get_subfields(code):
                    header = field.tag + "_" + code
                    if header in record_dict:
                        #print(f"Repeated subfield {code} in {field_to_csv}")
                        record_dict[header] = f"{record_dict[header]};{subfield}"
                    else:
                        record_dict[header] = subfield
        else:
            header = field.tag
            record_dict[header] = field.value()


    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,"source_path","", "FileChooser")
        ServiceTaskBase.add_argument(parser,"save_to_file","", "DirChooser")
        ServiceTaskBase.add_argument(parser,"fields_to_csv","A list of fields. Each occurence of the first field will be represented by a row.","")
    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "source_path", "")
        ServiceTaskBase.add_cli_argument(parser, "save_to_file", "")
        ServiceTaskBase.add_cli_argument(parser, "fields_to_csv","A list of fields. Each occurence of the first field will be represented by a row.")
