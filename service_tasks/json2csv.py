from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import sys, csv, json
import pandas as pd

class JSONtoCSV(ServiceTaskBase):
    def __init__(self, args):
        self.jsonfile = args.jsonfile
        self.csvfile = self.jsonfile[:-4] + "csv"

    def do_work(self):
        df = pd.read_json(self.jsonfile)
        root_element = df.keys()[0]

        source_data = df[root_element]

        data_file = open(self.csvfile, 'w', newline='')
        csv_writer = csv.writer(data_file) 

        count  = 0
        
        for record in source_data:
            if count == 0:
                # write headers
                header = record.keys()
                csv_writer.writerow(header)
                count += 1

            next_record = []

            for field in header:
               next_record.append(str(record[field]))

            csv_writer.writerow(next_record)

        data_file.close()
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "jsonfile", "JSON file to convert to CSV", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_argument(parser, "jsonfile", "JSON file to convert to CSV", "FileChooser")
