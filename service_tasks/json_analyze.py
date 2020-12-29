from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import json, sys

class ListJSONkeys(ServiceTaskBase):
    def __init__(self, args):
        self.json_file = args.json_file

    def do_work(self):
        def walk_keys(obj, path = ""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    for r in walk_keys(v, path + "." + k if path else k):
                        yield r
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    s = ""
                    for r in walk_keys(v, path if path else s):
                        yield r
            else:
                yield path

        with open(self.json_file) as json_file:
            json_data = json.load(json_file)

            all_keys = list(set(walk_keys(json_data)))

            print('\n'.join([str(x) for x in sorted(set(all_keys))]))

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "json_file", "JSON file", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_argument(parser, "json_file", "JSON file", "FileChooser")
