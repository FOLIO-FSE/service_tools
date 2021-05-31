import argparse
import csv
import pathlib
import json
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class CsvToJson(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.file_to_index = args.file_to_index
        self.index_name = args.index_name

    def do_work(self):
        index = 0
        with open(self.file_to_index) as datafile:
            csv.register_dialect("tsv", delimiter="\t")
            reader = csv.DictReader(datafile, dialect='tsv')
            for line in reader:
                index += 1
                payload.append(json.dumps(
                    {"index": {"_index": self.index_name, "_id": index}}))
                payload.append('\n')
                payload.append(line)
                if index % 500 == 0:
                    print(f"posting {index}")
                    response = requests.post('http://127.0.0.1:9200/_bulk',
                                             data=''.join(payload) + '\n',
                                             headers={"Content-Type": 'application/x-ndjson'})
                    print(response.status_code, flush=True)
                    if (str(response.status_code).startswith('4') or
                            str(response.status_code).startswith('5')):
                        print(response.text)
                        print(json.dumps(response.json))
                    payload = []

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "file_to_index",
                                     "File to load into Elasticsearch",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser,
                                     "index_name",
                                     "Name of the Elastic Index", ""
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "file_to_index",
                                         "File to load into Elasticsearch")
        ServiceTaskBase.add_cli_argument(parser,
                                         "index_name",
                                         "Name of the Elastic Index")
