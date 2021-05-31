import json
from abc import abstractmethod

import xmltodict as xmltodict

from service_tasks.service_task_base import ServiceTaskBase


class XML2JSON(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.from_file = args.from_file
        self.to_file = args.to_file

    def do_work(self):
        with open(self.to_file, 'w+') as outfile:
            xml_file = open(self.from_file, 'r').read()
            o = xmltodict.parse(xml_file)
            json.dump(o, outfile, indent=4)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "from_file",
                                     "The XML file you want to transform to JSON",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser,
                                     "to_file",
                                     "The destination where you want to store the results",
                                     "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "from_file",
                                         "The XML file you want to transform to JSON")
        ServiceTaskBase.add_cli_argument(parser,
                                         "to_file",
                                         "The destination where you want to store the results")
