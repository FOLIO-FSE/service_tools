import argparse
import os
import pathlib
import json
from abc import abstractmethod
from sickle import Sickle
import requests
import codecs

from service_tasks.service_task_base import ServiceTaskBase


class OAIHarvest(ServiceTaskBase):
    def __init__(self, args):
        self.set_name = "all"
        self.base_uri = args.base_uri
        self.from_date = args.from_date
        self.results_folder = args.results_folder
        self.metadata_prefix = args.metadata_prefix

    def do_work(self):
        sickle = Sickle(self.base_uri, timeout=36000)
        identify = sickle.Identify()
        print(identify.repositoryName)
        formats = [f.metadataPrefix for f in sickle.ListMetadataFormats()]
        if self.metadata_prefix not in formats:
            print(f"{self.metadata_prefix} is not amongst accepted metadata formats ({formats}")
            raise ValueError("metadata format")
        records = sickle.ListRecords(metadataPrefix=self.metadata_prefix, set='all')
        i = 0
        with codecs.open(os.path.join(self.results_folder, f"{i}.json"), "w+", "utf-8") as harvest_file:
            for record in records:
                i += 1
                if i % 10 == 0:
                    print(i)

                try:
                    harvest_file.write(record.raw.replace("<marc:", "<").replace("</marc:", "</"))
                except Exception as ee:
                    print(ee)
                    print(record.raw)
        print("Finished!")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "results_folder",
                                     "Folder where results are saved",
                                     "DirChooser")
        ServiceTaskBase.add_argument(parser,
                                     "base_uri",
                                     "Base uri of the OAI server", ""
                                     )

        ServiceTaskBase.add_argument(parser,
                                     "metadata_prefix",
                                     "Metadata prefix", ""
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "from_date",
                                     "From date", ""
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "results_folder",
                                         "Folder where results are saved")
        ServiceTaskBase.add_cli_argument(parser,
                                         "base_uri",
                                         "Base uri of the OAI server")

        ServiceTaskBase.add_cli_argument(parser,
                                         "metadata_prefix",
                                         "Metadata prefix")
        ServiceTaskBase.add_cli_argument(parser,
                                         "from_date",
                                         "From date")
