from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import pandas as pd, re

class CountRegExOccurrences(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.input_file = args.input_file
        self.regex_wanted = args.regex_wanted

    def do_work(self):
        print(f"Occurrences of {self.regex_wanted} in reverse frequency order") 
        with open (self.input_file, "r", encoding="utf8") as inputfile:
            searchdata=inputfile.read()

        regex = re.compile(self.regex_wanted, re.IGNORECASE)
        regex_list = re.findall(regex, searchdata)
        series = pd.Series(regex_list)
        print(series.value_counts())

            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "input_file", "File to analyze", "FileChooser")
        ServiceTaskBase.add_argument(parser, "regex_wanted", "Regular expression to match", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "input_file", "File to analyze")
        ServiceTaskBase.add_cli_argument(parser, "regex_wanted", "Regular expression to match")
