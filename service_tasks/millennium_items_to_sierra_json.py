import json
import re
from abc import abstractmethod
from os import listdir
from os.path import isfile, join

from service_tasks.service_task_base import ServiceTaskBase


class MillenniumItemsToSierraJson(ServiceTaskBase):
    def __init__(self, args):
        self.millenium_items_path = args.data_path
        self.result_path = args.result_path
        self.sierra_items = {}

    def do_work(self):
        print("here!")
        with open(self.millenium_items_path, "r") as millenium_items_file:
            for r in millenium_items_file:
                columns = r.split('","')
                index_of_i = [i for i, item in enumerate(columns) if re.search('i[0-9]{7}[0-9x]', item)]
                b_numbers = columns[:index_of_i]
                if len(b_numbers) > 1:
                    print("b_numbers")

        '''    temp_map = json.load(file)
            print(f"{len(temp_map)} items in map")
            self.results.update(temp_map)
            print(f"{len(self.results)} items in joint map")
        with open(join(self.result_path, "id_map_joined.json"), "w+") as res_file:
            res_file.write(json.dumps(self.results))'''
        print(f"Done!  ")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "data_path", "Path to the file", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Path to the file", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="path to millenium file")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="path to results file")
