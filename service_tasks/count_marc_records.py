import time
from abc import abstractmethod

from pymarc import MARCReader

from service_tasks.service_task_base import ServiceTaskBase


class CountMarcRecords(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.marc_file = args.marc_file

    def do_work(self):
        start = time.time()
        print(f"processing {self.marc_file}", flush=True)
        with open(self.marc_file, "rb") as marc_file:
            reader = MARCReader(marc_file, "rb")
            reader.hide_utf8_warnings = True
            for idx, marc_record in enumerate(reader):
                if idx % 1000 == 0:
                    elapsed = idx / (time.time() - start)
                    elapsed_formatted = "{0:.3g}".format(elapsed)
            print(idx)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "marc_file", "URL To MARC file", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "marc_file", "URL To MARC file")
