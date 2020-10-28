import json
import traceback
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class BatchPoster(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.failed_ids = []
        self.api_path = list_objects()[args.object_name]
        self.object_name = args.object_name
        self.failed_objects = []
        self.batch_size = args.batch_size
        self.processed = 0
        self.processed_rows = 0
        self.objects_file = args.objects_file
        self.users_per_group = {}
        self.failed_fields = set()
        self.num_failures = 0
        self.start = 0  # TODO: add this as an argument

    def do_work(self):
        print("Starting....")
        batch = []

        with open(self.objects_file) as rows:
            for row in rows:
                self.processed_rows += 1
                if self.processed_rows > self.start:
                    continue
                try:
                    json_rec = json.loads(row.split("\t")[-1])
                    batch.append(json_rec)
                    if len(batch) == int(self.batch_size):
                        self.post_batch(batch)
                        batch = []
                except Exception as exception:
                    print(f"{exception} row failed", flush=True)
                    batch = []
                    traceback.print_exc()
                    self.num_failures += 0
                    if self.num_failures > 5:
                        print(f"Exceeded number of failures at row {idx}")
                        raise exception
            # Last batch
        self.post_batch(batch)
        print(json.dumps(self.failed_objects), flush=True)
        print(json.dumps(self.failed_ids, indent=4), flush=True)

    def post_batch(self, batch, repost=False):
        response = self.do_post(batch)
        if response.status_code == 201:
            print(
                f"Posting successful! {self.processed_rows} {response.elapsed.total_seconds()}s {len(batch)}",
                flush=True,
            )
        elif response.status_code == 422:
            print(f"{response.status_code}\t{response.text}")
            resp = json.loads(response.text)

            for error in resp["errors"]:
                self.failed_fields.add(error["parameters"][0]["key"])
                self.failed_ids.append(error["parameters"][0]["value"])
            print(f"1 {len(batch)}")
            self.handle_failed_batch(batch)
            """if not repost:
                self.handle_failed_batch(batch)
            else:
                raise Exception(f"Reposting despite handling. {self.failed_ids}")"""
        elif response.status_code in [500, 413]:
            # Error handling is sparse. Need to identify failing records
            print(f"{response.status_code}\t{response.text}")
            if not len(batch) == 1:
                # split the batch in 2
                my_chunks = chunks(batch, 2)
                for chunk in my_chunks:
                    print(f"chunks with {len(chunk)} objects. " "posting chunk...")
                    self.post_batch(chunk)
            else:
                print(
                    f"Only one object left. Adding {batch[0]['id']} to failed_objects"
                )
                self.failed_objects = batch[0]
        else:
            raise Exception(f"ERROR! HTTP {response.status_code}\t{response.text}")

    def handle_failed_batch(self, batch):
        # new_batch = [f for f in batch]  # if f["instanceId"] not in self.failed_ids]
        ff = list(self.failed_fields)
        if "holdingsrecordid" in ff:
            new_batch = [
                f for f in batch if (f["holdingsRecordId"] not in self.failed_ids)
            ]
        elif "instanceid" in ff:
            new_batch = [f for f in batch if f["instanceId"] not in self.failed_ids]
        else:
            raise Exception(f"unhandled failed fields: {ff}")
        # print(f"2 {len(batch)}")
        """
        for it in batch:
            batch_string = json.dumps(it)
            for id in self.failed_ids:
                if id in batch_string:
                    print(f"id found {id}, removing.")
                elif it not in new_batch:
                    new_batch.append(it)"""
        print(
            f"re-posting new batch {len(self.failed_ids)} {len(batch)} {len(new_batch)}",
            flush=True,
        )
        self.post_batch(new_batch, True)

    def do_post(self, batch):
        kind = list_objects()[self.object_name]
        path = kind["api_endpoint"]
        url = self.folio_client.okapi_url + path
        if kind["total_records"]:
            payload = {"records": list(batch), "totalRecords": len(batch)}
        else:
            payload = {kind["object_name"]: batch}
        # print(json.dumps(payload, ensure_ascii=True))
        return requests.post(
            url, data=json.dumps(payload), headers=self.folio_client.okapi_headers
        )

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "objects_file", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(parser, "batch_size", "batch size", "")
        ServiceTaskBase.add_argument(parser, "object_name", "What objects to batch post", "Dropdown",
                                     metavar='What objects to batch post',
                                     dest='object_name',
                                     choices=list(list_objects().keys()),
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "objects_file", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "batch_size", "batch size")
        ServiceTaskBase.add_cli_argument(parser, "object_name", "What objects to batch post",
                                         choices=list(list_objects().keys())
                                         )


def list_objects():
    return {
        "Items": {"object_name": "items", "api_endpoint": "/item-storage/batch/synchronous", "total_records": False},
        "Holdings": {"object_name": "holdingsRecords", "api_endpoint": "/holdings-storage/batch/synchronous",
                     "total_records": False},
        "Instances": {"object_name": "instances", "api_endpoint": "/instance-storage/batch/synchronous",
                      "total_records": False},
        "Source Records - Batch": {"object_name": "records", "api_endpoint": "/source-storage/batch/records",
                                   "total_records": True},
        "InventoryInstances": {"object_name": "instances", "api_endpoint": "/inventory/instances/batch",
                               "total_records": False},
    }


def chunks(records, number_of_chunks):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(records), number_of_chunks):
        yield records[i: i + number_of_chunks]
