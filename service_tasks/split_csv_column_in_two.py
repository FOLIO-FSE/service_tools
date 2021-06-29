import csv

import pandas as pd

from service_tasks.service_task_base import ServiceTaskBase


class SplitCsvColumnInTwo(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.delimited_file = args.delimited_file
        self.separator = args.separator
        self.split_column = args.split_column
        self.left_column = args.left_column
        self.right_column = args.right_column
        self.save_to_file = args.save_to_file
        self.format = args.format

    def do_work(self):
        print("Let's get started!")
        if self.format == "csv":
            try:
                data = pd.read_csv(self.delimited_file, dtype=object)
            except UnicodeDecodeError as e:
                data = pd.read_csv(self.delimited_file, dtype=object, encoding="unicode_escape")
                print("Error decoding file. Try reding it with encoding='unicode_escape'")
        if self.format == "tsv":
            data = pd.read_csv(self.delimited_file, sep="\t", dtype=object)

        split_data = data[self.split_column].str.split(self.separator, n=1, expand=True)

        data.drop(columns=[self.split_column], inplace=True)

        data[self.left_column] = split_data[0]
        data[self.right_column] = split_data[1]
        if self.format == "tsv":
            data.to_csv(self.save_to_file, index=False, sep="\t")
        else:
            data.to_csv(self.save_to_file, index=False, quoting=csv.QUOTE_ALL)

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "delimited_file",
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
                                     "The name of the new column where we'll put data found to the left of the separator.",
                                     ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "right_column",
                                     "The name of the new column where we'll put data found to the right of the separator.",
                                     ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_file",
                                     "Path to output file.", ""),
        ServiceTaskBase.add_argument(sub_parser,
                                     "format",
                                     "Format of the data to analyse.",
                                     widget='Dropdown',
                                     choices=["csv", "tsv"])

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "delimited_file",
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
                                         "Path to output file.")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "format",
                                         "Format of the data to analyse: csv or tsv")
