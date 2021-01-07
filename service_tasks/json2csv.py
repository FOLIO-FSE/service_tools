from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import sys, csv, json
import pandas as pd

class JSONtoCSV(ServiceTaskBase):
    def __init__(self, args):
        self.jsonfile = args.jsonfile
        self.csvfile = self.jsonfile[:-4] + "csv"

    def do_work(self):
        df = pd.read_json(self.jsonfile)
        source_data = df.from_records(df["data"])

        print(source_data)

        source_data.to_csv(self.csvfile, index=False) 
        print(f"Records are written to {self.csvfile}") 
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "jsonfile", "JSON file to convert to CSV", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_argument(parser, "jsonfile", "JSON file to convert to CSV", "FileChooser")
