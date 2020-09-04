import uuid
import time
from abc import abstractmethod

import requests
from pymarc import MARCReader

from service_tasks.service_task_base import ServiceTaskBase


class CountMarcRecords(ServiceTaskBase):
    def __init__(self, folio_client, path_to_marc_records):
        super().__init__(folio_client)
        self.path_to_marc_records = path_to_marc_records

    def do_work(self):
        start = time.time()
        print(f"processing {self.path_to_marc_records}", flush=True)
        with open(self.path_to_marc_records, "rb") as marc_file:
            reader = MARCReader(marc_file, "rb")
            reader.hide_utf8_warnings = True
            for idx, marc_record in enumerate(reader):
                if idx % 1000 == 0:
                    elapsed = idx / (time.time() - start)
                    elapsed_formatted = "{0:.3g}".format(elapsed)
            print(idx)

    @staticmethod
    @abstractmethod
    def add_arguments(sub_parser):
        sub_parser.add_argument(
            "marc_file", help="URL To MARC file", widget="FileChooser"
        )
