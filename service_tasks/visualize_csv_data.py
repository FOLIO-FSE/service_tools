import csv
import pandas
import matplotlib.pyplot as plt
from service_tasks.service_task_base import ServiceTaskBase


class VisualizeCsvData(ServiceTaskBase):
# Open file and read into a Pandas Dataframe
    def __init__(self, args):
        print("Let's get started!")
        self.csv_file = args.csv_file
        self.save_to_folder = args.save_to_folder

    def do_work(self):
        with open(self.csv_file) as file:
            data = pandas.read_csv(file, sep=",")

        # Create a bar chart showing how many times a field occurs in the data
        plt.rcParams["font.size"] = 12.0
        data.count().plot.barh(figsize=(10, 10), color = "royalblue")
        plt.title("Field occurences")
        plt.savefig(save_to_folder + "field_occurences.svg")

        for column in data.columns:
        # Show number of occurences for each unique value per column (truncated if many)
        value_counts = data[column].value_counts()
        value_names_raw = value_counts.index.tolist()
        rint(f"{column}\n{value_counts}\n\n")    
        
        if value_counts.any():
            value_names = [str(name).replace("$","|") for name in value_names_raw]
            # Creating plot 
            fig = plt.figure(figsize =(13, 10))
            plt.title(column)
            pieces, values = plt.pie(value_counts, labels = value_names, colors = plt.cm.tab20.colors)
            plt.legend(pieces, value_names[:10], loc="best")

            # Save plot as svg image
            filename = column.replace(" ","_") + ".svg"
            plt.savefig(save_to_folder + filename)

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)

        ServiceTaskBase.add_argument(sub_parser,
                                     "csv_file",
                                     "The csv file to be analyzed. All rows must have the same number of columns.",
                                     "FileChooser")
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved. E.g. c:/thisplace/thatfolder",
                                     "FileChooser")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "csv_file",
                                         "The csv file to be analyzed. All rows must have the same number of columns. c:/thisplace/thatfolder")
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved."
