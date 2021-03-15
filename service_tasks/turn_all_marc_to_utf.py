import time
from abc import abstractmethod

from pymarc import MARCReader, Record

from service_tasks.service_task_base import ServiceTaskBase


class TurnAllMarcToUTF(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.marc_file = args.marc_file

    def do_work(self):
        start = time.time()
        print(f"processing {self.marc_file}", flush=True)
        reader = MARCReader(open(self.marc_file, "rb"), to_unicode=True)
        for idx, marc_record in enumerate(reader):
            self.set_leader(marc_record)
            print(marc_record)

            print(idx)
        reader.close()

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "marc_file", "URL To MARC file", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "marc_file", "URL To MARC file")

    @staticmethod
    def set_leader(marc_record:Record):
        new_leader = marc_record.leader
        marc_record.leader = new_leader[:9] + 'a' + new_leader[10:]

