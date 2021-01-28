import csv
import pandas
import matplotlib.pyplot as plt
from mdutils.mdutils import MdUtils
from service_tasks.service_task_base import ServiceTaskBase


class VisualizeCsvData(ServiceTaskBase):
# Open file and read into a Pandas Dataframe
    def __init__(self, args):
        print("Let's get started!")
        self.csv_file = args.csv_file
        self.save_to_folder = args.save_to_folder
        self.mdFile = MdUtils(file_name=self.save_to_folder + "/" + "report.md", title='ILS data field analysis')


    def do_work(self):
        with open(self.csv_file) as file:
            print("Analyzing data...")
            data = pandas.read_csv(file, sep=",", dtype=object)

        self.mdFile.new_header(level=1, title='ILS data field analysis')

        self.mdFile.new_paragraph("Scroll down to learn about your legacy data.")

        try:
            # Print overview to md file
            self.mdFile.new_header(level=2, title="Data overview")
            self.mdFile.new_paragraph(f"Your file contains {len(data.index)} rows (records) and {len(data.columns)} columns (fields). These are the present fields:")
            self.mdFile.new_paragraph(f"These are the present fields:")
            for name in data.columns.values:
                self.mdFile.new_line(str(name))

            # Create a bar chart showing how many times a field occurs in the data
            plt.rcParams["font.size"] = 12.0
            data.count().plot.barh(figsize=(10, 10), color = "royalblue")
            plt.title("Field occurences")

            filename = "field_occurences.svg"
            filepath = self.save_to_folder + "/" + filename
            plt.savefig(filepath)
            plt.close()
            self.mdFile.new_line(self.mdFile.new_inline_image(text= "Chart", path=filename))
            self.mdFile.new_paragraph(f"**Nubmer of non-empty fields**\n{data.notnull().sum()}")
            self.mdFile.new_paragraph(f"**Nubmer of empty fields**\n{data.isnull().sum()}")

            self.mdFile.new_header(level=2, title="A closer look at the different fields")


            print("Making pie charts...")

            # Show number of occurences for each unique value per column (truncated if many)
            for column in data.columns:
                value_counts = data[column].value_counts()
                value_names_raw = value_counts.index.tolist()
                value_counts_dict = value_counts.to_dict()

                self.mdFile.new_header(level=3, title=column)
                unique_values = data[column].nunique()
                print(f"Unique values in {column}: {unique_values}")

                
                if 1 <= unique_values <= 100:
                    string_value_counts = []
                    for value in value_counts_dict:
                        string_value_counts.append(f"{value}   {value_counts[value]}\n")

                    value_names = [str(name).replace("$","|") for name in value_names_raw]
                    # Creating plot 
                    plt.figure(figsize =(14, 7))
                    plt.title(column)
                    plt.tight_layout()
                    plt.pie(value_counts, labels = value_names, colors = plt.cm.tab20.colors)
                    plt.legend(string_value_counts, loc="center left", bbox_to_anchor=(1, 0.5))

                    # Save plot as svg image
                    filename = column.replace(" ","_") + ".svg"
                    filepath = self.save_to_folder + "/" + filename
                    plt.savefig(filepath)
                    plt.close()

                    self.mdFile.new_line(self.mdFile.new_inline_image(text= "Chart", path=filename))
                
                else:
                    dupe_dict = value_counts[value_counts > 1].to_dict()
                    md_dupes = []
                    for value in dupe_dict:
                        md_dupes.append(f"{value_counts[value]} ............... {value}")

                    self.mdFile.new_paragraph(f"\nThis field has {unique_values} unique values, out of {len(data.index)} occurences (including null/undefined). Non-unique values may be duplicates.")
                    self.mdFile.new_paragraph("**# ............... Value**")
                    for row in md_dupes:
                        self.mdFile.new_line(f"{row}")
        except Exception as e:
            print(e)

        finally:
            self.mdFile.new_table_of_contents(table_title='Contents', depth=3)
            self.mdFile.create_md_file()


    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "csv_file",
                                     "The csv file to be analyzed. All rows must have the same number of columns.",
                                     "FileChooser")
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "csv_file",
                                         "The csv file to be analyzed. All rows must have the same number of columns. c:/thisplace/thatfolder")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.")