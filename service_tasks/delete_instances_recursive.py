import uuid
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase



class DeleteInstancesRecursive(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.instances_to_delete = args.instance_ids
        self.dry_run = False # args.dry_run

    def do_work(self):
        stubrecord = ""
        instance_ids = self.instances_to_delete.split(',')
        print(f"Working on deleting {len(instance_ids)} instances")
        for instance_id in [id.strip() for id in instance_ids if id]:
            if not uuid.UUID(instance_id) and not uuid.UUID(instance_id).version >= 4:
                raise Exception(f"id {instance_id} of Object to delete is not a proper UUID")
            #instance_to_delete = self.folio_client.folio_get_single_object(f"/instance-storage/instances/{instance_id}")
            
            instance_to_delete = self.folio_client.folio_get_single_object(f"/inventory/items?query=instance.id=={instance_id}")
            print(f"Processing instance {instance_id}")
            self.delete_items(instance_to_delete)

            query = f'?query=(instanceId="{instance_id}")'
            holdings = list(self.folio_client.get_all("/holdings-storage/holdings", "holdingsRecords", query))
            self.delete_holdings(holdings)
            
            srs = self.folio_client.folio_get_single_object(f"/source-storage/records/{instance_id}/formatted?idType=INSTANCE")
            self.delete_srs(srs)
            print(f"Deleting instance {instance_id}")
            self.delete_request("/instance-storage/instances", instance_id)
            stubrecord += "=LDR  00000dam  2200000Ia 4500\n=999  ff$i" + instance_id + "\n\n"

        print(f"The stub record(s) below can be pasted into Marcedit to create records tofacilitate record deletion in EDS\n-------------------------------\n")
        print(stubrecord)

    def delete_items(self, instance_to_delete):
        item_iterator = 0
        totalRecords = 0

        totalRecords = instance_to_delete["totalRecords"]

        if totalRecords > 0: 
            while item_iterator < totalRecords:
                print("start item process")
                item = instance_to_delete["items"][item_iterator]["id"]
                holding = instance_to_delete["items"][item_iterator]["holdingsRecordId"]
                item_iterator += 1
                print("Deleting item: " + item + " associated with holding ID " + holding)
                self.delete_request("/item-storage/items", item)
        else:
            print("No items detected")
	
    def delete_holdings(self, holdings):
        holding_iterator = 0
        
        if holdings:
            for holding in holdings:
                holding = holding["id"]
                print("Deleting holding: " + holding)
                self.delete_request(f"/holdings-storage/holdings", holding)
        else:
            print("No holdings detected")

    def delete_srs(self, srs):
        id = srs["id"]

        if id is not None:
            print("Deleting SRS: " + id)
            self.delete_request(f"/source-storage/records", id)
        else:
            print("No SRS detected")

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
