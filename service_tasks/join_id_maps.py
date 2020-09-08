import json
from abc import abstractmethod
from os import listdir
from os.path import isfile, join

from service_tasks.service_task_base import ServiceTaskBase


class JoinIdMaps(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.data_path = args.data_path
        self.result_path = args.result_path
        self.results = {}

    def do_work(self):
        files = [f for f in self.data_path.split(';') if isfile(f)]
        for file_name in files:
            self.add_stats("Files to join")
            with open(file_name, "r") as file:
                temp_map = json.load(file)
                print(f"{len(temp_map)} items in map")
                self.results.update(temp_map)
                print(f"{len(self.results)} items in joint map")
        with open(join(self.result_path, "id_map_joined.json"), "w+") as res_file:
            res_file.write(json.dumps(self.results))
        print(f"Done!  ")
        self.print_dict_to_md_table(self.stats)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
            "data_path", help="path to folder with files to map", widget="MultiFileChooser"
        )
        ServiceTaskBase.add_argument(parser,"result_path", help="path to resutls file", widget="DirChooser")
