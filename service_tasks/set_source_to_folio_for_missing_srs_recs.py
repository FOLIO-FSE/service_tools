import json
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class SetSourceToFOLIOForMissingSRSRecs(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.instance_ids = []
        with open(args.source_file) as missing_srs_file:
            for line in missing_srs_file:
                self.instance_ids.append(line.strip())
        print(f"Number of records to update: {len(self.instance_ids)}")
        self.id_map = {}

    def do_work(self):
        i = 0
        for instance_id in self.instance_ids:
            i += 1
            if i % 100 == 0:
                print(i)
            url = f"{self.folio_client.okapi_url}/instance-storage/instances/{instance_id}"
            resp = requests.get(url, headers=self.folio_client.okapi_headers)
            instance = json.loads(resp.text)
            if instance["source"] != "FOLIO":
                instance["source"] = "FOLIO"
                req = requests.put(url, headers=self.folio_client.okapi_headers, data=json.dumps(instance))
                print(req.status_code)
                print(req.text)
                req.raise_for_status()
        print_dict_to_md_table(self.stats)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,destination=
            "source_file", help="file of Instance Ids to be updated", widget="FileChooser"
        )
