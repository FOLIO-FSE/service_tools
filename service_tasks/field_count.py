from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import sys, csv
import pandas as pd

class CountOccurrences(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.csv_file = args.csv_file
        self.field_wanted = args.field_wanted

    def do_work(self):
        print(f"Occurrences of {self.field_wanted} in reverse frequency order") 
        field_values = pd.read_csv(self.csv_file, encoding = 'unicode_escape', engine ='python')
        print(field_values[self.field_wanted].value_counts())

            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "csv_file", "Delimited file containing field to analyze", "FileChooser")
        ServiceTaskBase.add_argument(parser, "field_wanted", "Name of field to analyze, must be at top of column", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "csv_file", "Delimited file containing field to analyze")
        ServiceTaskBase.add_cli_argument(parser, "field_wanted", "Name of field to analyze, must be at top of column")
