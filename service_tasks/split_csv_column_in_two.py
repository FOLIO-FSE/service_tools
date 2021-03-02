import csv
import pandas as pd
from service_tasks.service_task_base import ServiceTaskBase


class SplitCsvColumnInTwo(ServiceTaskBase):
    def __init__(self, args):
        self.csv_file = args.csv_file
        self.separator = args.separator
        self.split_column = args.split_column
        self.left_column = args.left_column
        self.right_column = args.right_column
        self.save_to_file = args.save_to_file


    def do_work(self):
        print("Let's get started")
        try: 
            data = pd.read_csv(self.csv_file, dtype=object)      
        except UnicodeDecodeError as e:
            data = pd.read_csv(self.csv_file, dtype=object, encoding="unicode_escape")
        
        split_data = data[self.split_column].str.split(self.separator, n = 1, expand = True) 
        
        data[self.left_column]= split_data[0]
        data[self.right_column]= split_data[1]
 
        data.drop(columns =[self.split_column], inplace = True)

        data.to_csv(self.save_to_file, index=False, quoting=csv.QUOTE_ALL)

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "csv_file",
                                     "The csv file to be analyzed. All rows must have the same number of columns.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "split_column",
                                     "The column with the data you want to split.", ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "separator",
                                     "The separator you want to split the column by.", ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "left_column",
                                     "The name of the new column where we'll put data found to the left of the separator.", ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "right_column",
                                     "The name of the new column where we'll put data found to the right of the separator.", ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_file",
                                     "Name of output file.", "")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "csv_file",
                                         "The csv file to be analyzed. All rows must have the same number of columns."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "split_column",
                                     "The column with the data you want to split."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "separator",
                                     "The separator you want to split the column by."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "left_column",
                                     "The name of the new column where we'll put data found to the left of the separator."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "right_column",
                                     "The name of the new column where we'll put data found to the right of the separator."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_file",
                                     "Output file.")