import uuid
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class DeleteInstances(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.instances_to_delete = args.instances_to_delete
        self.dry_run = args.dry_run

    def do_work(self):
        instance_ids = self.instances_to_delete.split(',')
        print(f"Working on deleting {len(instance_ids)} instances")
        for instance_id in [id.strip() for id in instance_ids]:
            if not uuid.UUID(instance_id) and not uuid.UUID(instance_id).version >= 4:
                raise Exception(f"id {instance_id} of Object to delete is not a proper UUID")
            instance_to_delete = self.folio_client.folio_get_single_object(f"/instance-storage/instances/{instance_id}")
            print(f'Will delete {instance_to_delete["title"]}. Just checking for holdings first')
            query = f'?query=(instanceId="{instance_id}")'
            holdings = self.folio_client.get_all("/holdings-storage/holdings", "holdingsRecords", query)
            if len(holdings) > 0:
                print(f"{len(holdings)} attached found. Halting. Delete holdings and other attached records first")
            else:
                print("No holdings found. Deleting Instance")
                self.delete_request("/instance-storage/instances", instance_id)

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
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        sub_parser.add_argument(
            "-d", "--dry_run", action="store_true", help="Dry run only"
        )
        sub_parser.add_argument(
            "instance_ids",
            help="Comma separated list of instance ids " "to delete",
            widget="Textarea",
        )
