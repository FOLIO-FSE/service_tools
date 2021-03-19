import csv
import json
import pandas
import matplotlib.pyplot as plt
from mdutils.mdutils import MdUtils
from service_tasks.service_task_base import ServiceTaskBase
import traceback


class VisualizeCsvData(ServiceTaskBase):
# Open file and read into a Pandas Dataframe
    def __init__(self, args):
        print("Let's get started!")
        self.data_file = args.data_file
        self.save_to_folder = args.save_to_folder
        self.format = args.format
        self.mdFile = MdUtils(file_name=self.save_to_folder + "/" + "report.md", title='ILS data field analysis')


    def do_work(self):
        with open(self.data_file) as file:
            print("Analyzing data...")
            if self.format == "csv":
                data = pandas.read_csv(file, sep=",", dtype=object)
            if self.format == "tsv":
                data = pandas.read_csv(file, sep="\t", dtype=object)
            elif self.format == "json":
                json_data = json.load(file)
                data = pandas.json_normalize(json_data, max_level=2)

        self.mdFile.new_header(level=1, title='ILS data field analysis')

        self.mdFile.new_paragraph("Scroll down to learn about your legacy data.")

        try:
            # Print overview to md file
            self.mdFile.new_header(level=2, title="Data overview")
            self.mdFile.new_paragraph(f"Your file contains {len(data.index)} rows (records) and {len(data.columns)} columns (fields). These are the present fields:")
            self.mdFile.new_paragraph(f"These are the present fields:")
            self.mdFile.new_line(str(data.columns.values))

            # Create a bar chart showing how many times a field occurs in the data
            plt.rcParams["font.size"] = 12.0
            data.count().plot.barh(figsize=(10, 10), color = "royalblue")
            plt.title("Field occurences")

            filename = "field_occurences.svg"
            filepath = self.save_to_folder + "/" + filename
            plt.savefig(filepath)
            plt.close()
            self.mdFile.new_line(self.mdFile.new_inline_image(text= "Chart", path=filename))

            self.mdFile.new_header(level=2, title="A closer look at the different fields")


            print("Making pie charts...")

            # Show number of occurences for each unique value per column (truncated if many)
            for column in data.columns:
                value_counts = data[column].value_counts()
                value_names_raw = value_counts.index.tolist()
                value_counts_dict = value_counts.to_dict()

                self.mdFile.new_header(level=3, title=column)
                unique_values = data[column].nunique()
                self.mdFile.new_paragraph(f"Unique values in {column}: {unique_values}")

                print(f"Unique values in {column}: {unique_values}")

                if 1 <= unique_values <= 20:
                    string_value_counts = []
                    for value in value_counts_dict:
                        string_value_counts.append(f"{value}   {value_counts[value]}\n")

                    value_names = [str(name).replace("$","|") for name in value_names_raw]
                    # Creating plot 
                    plt.figure(figsize =(12, 8))
                    plt.title(column)
                    plt.tight_layout()
                    plt.pie(value_counts, labels = value_names, colors = plt.cm.tab20.colors)
                    plt.legend(string_value_counts, loc="center left", bbox_to_anchor=(1, 0.5))

                    # Save plot as svg image
                    filename = column.replace(" ","_") + ".svg"
                    filepath = self.save_to_folder + "/" + filename
                    plt.savefig(filepath)
                    plt.close()

                    tab_value_counts = value_counts.to_markdown()
                    self.mdFile.new_paragraph(tab_value_counts)

                    self.mdFile.new_paragraph(self.mdFile.new_inline_image(text= "Chart", path=filename))
                
                elif 21 <= unique_values <= len(data.index) / 10:
                    non_unique = value_counts[value_counts > 1]
                    tab_non_unique = non_unique.to_markdown()

                    self.mdFile.new_paragraph(f"\nOut of {len(data.index)} values (including null/undefined) in total, {unique_values} values are entirely unique. There are {len(non_unique)} reoccuring values. Recurring values may indicate duplicate data, or free text data that could be a controlled value.")
                    
                    if len(non_unique) <= 10:
                        self.mdFile.new_paragraph(tab_non_unique)
                    else:                
                        self.mdFile.new_paragraph(f"\n<details><summary>Expand to see a list of non-unique values.</summary>\n\n")
                        self.mdFile.new_paragraph(tab_non_unique)
                        self.mdFile.new_line("</details>\n")

        except Exception as e:
            print(e)
            traceback.print_exc() 

        finally:
            self.mdFile.new_table_of_contents(table_title='Contents', depth=3)
            self.mdFile.create_md_file()


    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "data_file",
                                     "The csv or json file to be analyzed. If csv, all rows must have the same number of columns.",
                                     "FileChooser")
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "format",
                                     "Format of the data to analyse.",
                                     widget='Dropdown',
                                     choices=["csv","tsv","json"])

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "data_file",
                                         "he csv or json file to be analyzed. If csv, all rows must have the same number of columns")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.")
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "format",
                                     "Format of the data to analyse.")                                     