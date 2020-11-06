import requests

from service_tasks.service_task_base import ServiceTaskBase


class IterateOverSRS(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("Init")

    def do_work(self):
        i = 0
        for srs_record in self.folio_client.folio_get_all('/source-storage/records', "records"):
            i+= 1
            if i%100 == 0:
                print(f"{i} records iterated")

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
