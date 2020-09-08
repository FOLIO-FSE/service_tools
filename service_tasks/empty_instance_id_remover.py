import json
from abc import abstractmethod
import requests
from os import listdir
from os.path import isfile, join

from service_tasks.service_task_base import ServiceTaskBase


class EmptyInstanceIdentifierRemover(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.instance_ids =[]

    def do_work(self):
        api_path = "/instance-storage/instances"
        query = f'?query=(identifiers=="*\\"value\\": \\"\\"*")'
        request_path = f"{api_path}"
        objects = self.folio_client.folio_get_all(api_path, "instances", query)
        print(len(objects))
        i = 0
        for instance in objects:
            i += 1
            self.add_stats("Instaces processed")
            l = len(instance["identifiers"])

            instance['identifiers'] = [f for f in instance['identifiers'] if
                                       f['value']]
            l2 = len(instance["identifiers"])
            if l>l2:
                print("posting updated instance")
                self.instance_ids.append(instance["id"])
                url = f'{self.folio_client.okapi_url}{api_path}/{instance["id"]}'
                req = requests.put(url, data=json.dumps(instance), headers=self.folio_client.okapi_headers)
                req.raise_for_status()
                print(req.status_code)
                self.add_stats("Instances posted")
        print(self.instance_ids)
        self.print_dict_to_md_table(self.stats)


    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
