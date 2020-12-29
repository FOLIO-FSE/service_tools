import json, uuid
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class DeleteRecords(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.records_to_delete = args.record_ids
        self.delete_type = args.form_data
        self.form_json =  json.dumps(list_objects()[args.form_data])
        json_doc = json.loads(self.form_json)
        self.api_endpoint = json_doc["api_endpoint"]

        self.dry_run = False # args.dry_run

    def do_work(self):
        record_ids = self.records_to_delete.split(',')
        print(f"Working on deleting {len(record_ids)} {self.delete_type} records")
        for record_id in [id.strip() for id in record_ids if id]:
            if not uuid.UUID(record_id) and not uuid.UUID(record_id).version >= 4:
                raise Exception(f"id {record_id} of Object to delete is not a proper UUID")

            self.delete_request(self.api_endpoint, record_id)

    def delete_request(self, path, record_id):
        parsed_path = path.rstrip("/").lstrip("/")
        url = f"{self.folio_client.okapi_url}/{parsed_path}/{record_id}"
        if not uuid.UUID(record_id) and not uuid.UUID(record_id).version >= 4:
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
        ServiceTaskBase.add_argument(parser, "form_data", "Record type to delete", "Dropdown", metavar='All attached records must be removed', dest='record_type', choices=list(list_objects().keys()),)
        ServiceTaskBase.add_argument(parser, "record_ids", "Comma separated list of record ids to delete", "Textarea") 

def list_objects():
    return {
            "Campuses": {"record_type": "campuses", "api_endpoint": "location-units/campuses"},
            "Holdings": {"record_type": "holdings", "api_endpoint": "holdings-storage/holdings"},
            "Instances": {"record_type": "instances", "api_endpoint": "instance-storage/instances"},
            "Items": {"record_type": "items", "api_endpoint": "item-storage/items"},
            "Libraries": {"record_type": "libraries", "api_endpoint": "location-units/libraries"},
            "Locations": {"record_type": "locations", "api_endpoint": "locations"},
            "Service points": {"record_type": "service_points", "api_endpoint": "service-points"},
            "Users": {"record_type": "users", "api_endpoint": "users"}
            }

