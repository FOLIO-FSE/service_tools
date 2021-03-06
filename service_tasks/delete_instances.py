import uuid
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class DeleteInstances(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.instances_to_delete = args.instance_ids
        self.dry_run = False # args.dry_run

    def do_work(self):
        instance_ids = self.instances_to_delete.split(',')
        print(f"Working on deleting {len(instance_ids)} instances")
        for instance_id in [id.strip() for id in instance_ids if id]:
            if not uuid.UUID(instance_id) and not uuid.UUID(instance_id).version >= 4:
                raise Exception(f"id {instance_id} of Object to delete is not a proper UUID")
            try:
                instance_to_delete = self.folio_client.folio_get_single_object(f"/instance-storage/instances/{instance_id}")
                print(f'Will delete {instance_to_delete["title"]}. Just checking for holdings first')
                query = f'?query=(instanceId="{instance_id}")'
                holdings = list(self.folio_client.get_all("/holdings-storage/holdings", "holdingsRecords", query))
                if len(holdings) > 0:
                    print(f"{len(holdings)} holding found attached to {instance_id}. Halting. Delete holdings and other attached records first")
                else:
                    print("No holdings found. Deleting instance.")
                    self.delete_request("/instance-storage/instances", instance_id)
            except requests.HTTPError as http_error:
                print(http_error)

    def delete_request(self, path, object_id):
        parsed_path = path.rstrip("/").lstrip("/")
        url = f"{self.folio_client.okapi_url}/{parsed_path}/{object_id}"
        if not uuid.UUID(object_id) and not uuid.UUID(object_id).version >= 4:
            raise Exception(f"id {object_id} of Object to delete is not a proper UUID")
        if not self.dry_run:
            print(f"DELETE {url}")
            req = requests.delete(url, headers=self.folio_client.okapi_headers)
            print(req.status_code)
            print(req.text)
            req.raise_for_status()
        else:
            print(f"Dry run: DELETE {url}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,
                                     "instance_ids",
                                     "Comma separated list of instance ids " "to delete",
                                     "Textarea"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser,
                                         "instance_ids",
                                         "Comma separated list of instance ids to delete"
                                         )
                                         