import json
from abc import abstractmethod
from os import listdir
from os.path import isfile, join

from service_tasks.service_task_base import ServiceTaskBase


class JoinIdMaps(ServiceTaskBase):
    def __init__(self, args):
        self.files = args.data_path
        self.result_path = args.result_path
        self.results = {}

    def do_work(self):
        print("here!")
        files = [
            join(self.files, f)
            for f in listdir(self.files)
            if isfile(join(self.files, f))
        ]
        print(files)
        for file_name in files:
            print(file_name)
            with open(file_name, "r") as file:
                temp_map = json.load(file)
                print(f"{len(temp_map)} items in map")
                self.results.update(temp_map)
                print(f"{len(self.results)} items in joint map")
        with open(join(self.result_path, "id_map_joined.json"), "w+") as res_file:
            res_file.write(json.dumps(self.results))
        print(f"Done!  ")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "data_path", "Path to the file", "DirChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Path to the file", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="path to folder with files to map")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="path to results file")
