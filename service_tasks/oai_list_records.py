import argparse
import io
import os
import pathlib
import traceback
import json
import xmltodict
from abc import abstractmethod

import pymarc
from sickle import Sickle
import requests
import codecs

from service_tasks.service_task_base import ServiceTaskBase


class OAIListIdentifiers(ServiceTaskBase):
    def __init__(self, args):
        self.set_name = "all"
        self.base_uri = args.base_uri
        self.from_date = args.from_date
        self.metadata_prefix = args.metadata_prefix

    def do_work(self):
        sickle = Sickle(self.base_uri, timeout=36000)
        identify = sickle.Identify()
        print(identify.repositoryName)
        formats = [f.metadataPrefix for f in sickle.ListMetadataFormats()]
        if self.metadata_prefix not in formats:
            print(f"{self.metadata_prefix} is not amongst accepted metadata formats ({formats}")
            raise ValueError("metadata format")
        records = sickle.ListIdentifiers(**{"metadataPrefix": self.metadata_prefix,
                                        "set": 'all', 'from': self.from_date})
        i = 0
        deleted = 0
        for record in records:
            i += 1

            try:
                if '<header status="deleted"' in record.raw:
                    deleted += 1
                    print(f'{i} \t DELETED')

                else:
                    o = xmltodict.parse(record.raw)
                    print(f'{i} \t {o["header"]["identifier"]}')
            except Exception as ee:
                print(ee)
                print(record.raw)
                traceback.print_exc()
        print("Finished!")
        print(f"Records fetched: {i}, of which are deleted: {deleted}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):

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
                                         "base_uri",
                                         "Base uri of the OAI server")

        ServiceTaskBase.add_cli_argument(parser,
                                         "metadata_prefix",
                                         "Metadata prefix")
        ServiceTaskBase.add_cli_argument(parser,
                                         "from_date",
                                         "From date")
