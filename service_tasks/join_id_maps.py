import argparse
import json
from abc import abstractmethod
from os import listdir
from os.path import isfile, join

from service_tasks.service_task_base import ServiceTaskBase
from folioclient import FolioClient


class JoinIdMaps(ServiceTaskBase):
    def __init__(self, args):
        self.data_path = args.data_path
        self.result_path = args.result_path
        print("\tFolder with files:\t", self.data_path)
        print("\tresults file:\t", self.result_path)
        self.results = {}

    def do_work(self):
        files = [f for f in listdir(self.data_path) if isfile(join(self.data_path, f))]
        for file_name in files:
            self.add_stats("Files to join")
            with open(join(self.data_path, file_name), "r") as file:
                temp_map = json.load(file)
                print(f"{len(temp_map)} items in map")
                self.results.update(temp_map)
                print(f"{len(self.results)} items in joint map")
        with open(self.result_path, "w+") as res_file:
            res_file.write(json.dumps(self.results))
        print(f"Done!  ")

    @staticmethod
    @abstractmethod
    def add_arguments(sub_parser):
        sub_parser.add_argument(
            "data_path", help="path to folder with files to map"
        )
        sub_parser.add_argument("result_path", help="path to resutls file")
