from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import csv
import pandas as pd

class JSONtoCSV(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.jsonfile = args.jsonfile
        self.csvfile = self.jsonfile[:-4] + "csv"

    def do_work(self):
        df = pd.read_json(self.jsonfile)

        root_element = df.keys()[0]
        # detect if using the reference backup tool, otherwise assume record is downloaded from FOLIO
        if root_element == 'name':
            source_data = df.from_records(df["data"])
        else:
            source_data = df.from_records(df[root_element])


        print(source_data)

        source_data.to_csv(self.csvfile, index=False) 
        print(f"Records are written to {self.csvfile}") 
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "jsonfile", "Reference data JSON file to convert to CSV", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "jsonfile", "Reference data JSON file to convert to CSV")
