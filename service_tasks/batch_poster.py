import json
import os
import traceback
from abc import abstractmethod
from datetime import datetime

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


def write_failed_batch_to_file(batch, file):
    for record in batch:
        file.write(f"{json.dumps(record)}\n")


class BatchPoster(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.failed_ids = []
        self.first_batch = True
        self.api_path = list_objects()[args.object_name]
        self.object_name = args.object_name
        self.failed_objects = []
        object_name_formatted = self.object_name.replace(" ", "").lower()
        self.log_path = os.path.join(args.results_folder, f'{object_name_formatted}_posting.log')
        self.failed_recs_path = os.path.join(args.results_folder, f'{object_name_formatted}_failed_records.json')
        self.batch_size = args.batch_size
        self.processed = 0
        self.failed_batches = 0
        self.failed_records = 0
        self.processed_rows = 0
        self.objects_file = args.objects_file
        self.users_per_group = {}
        self.failed_fields = set()
        self.num_failures = 0
        self.start = 0  # TODO: add this as an argument

    def do_work(self):
        print("Starting....")
        batch = []

        with open(self.objects_file) as rows, open(self.failed_recs_path, 'w') as failed_recs_file, open(
                self.log_path, 'w') as log_file:
            last_row = ""
            for idx, row in enumerate(rows):
                last_row = row
                if self.processed_rows < self.start:
                    continue
                if row.strip():
                    try:
                        self.processed_rows += 1
                        json_rec = json.loads(row.split("\t")[-1])
                        batch.append(json_rec)
                        if len(batch) == int(self.batch_size):
                            self.post_batch(batch)
                            batch = []
                    except UnicodeDecodeError as unicode_error:
                        print("=========ERROR==============")
                        print(f"{unicode_error} Posting failed. Encoding error reading file")
                        print(f"Failing row, either the one shown here or the next row in {self.objects_file}")
                        print(last_row)
                        print("=========Stack trace==============")
                        traceback.print_exc()
                        print("=======================", flush=True)
                    except Exception as exception:
                        print("=========ERROR==============")
                        print(f"Posting failed with the following error")
                        print(f"{exception} Posting failed")
                        print(f"Failing row, either the one shown here or the next row in {self.objects_file}")
                        print(last_row)
                        print("writing failed batch to file")
                        self.failed_batches += 1
                        self.failed_records += len(batch)
                        write_failed_batch_to_file(batch, failed_recs_file)
                        batch = []
                        print("=========Stack trace==============")
                        traceback.print_exc()
                        print("=======================", flush=True)
                        self.num_failures += 0
                        if self.num_failures > 50:
                            print(f"Exceeded number of failures at row {idx}")
                            raise exception
            # Last batch
        self.post_batch(batch)
        print(f"{self.failed_records} failed records in {self.failed_batches} saved to {self.failed_recs_path}")

    def post_batch(self, batch):
        response = self.do_post(batch)
        if response.status_code == 201:
            print(
                f"Posting successful! Total rows: {self.processed_rows}  {response.elapsed.total_seconds()}s "
                f"Batch Size: {len(batch)} Request size: {get_req_size(response)} "
                f"{datetime.utcnow().isoformat()} UTC",
                flush=True,
            )
        elif response.status_code == 422:
            resp = json.loads(response.text)
            raise Exception(
                f"HTTP {response.status_code}\t"
                f"Request size: {get_req_size(response)}"
                f"{datetime.utcnow().isoformat()} UTC\n"
                f"{json.dumps(resp, indent=4)}")
        else:
            raise Exception(
                f"HTTP {response.status_code}\t"
                f"Request size: {get_req_size(response)}"
                f"{datetime.utcnow().isoformat()} UTC\n"
                f"{response.text}")

    def do_post(self, batch):
        kind = list_objects()[self.object_name]
        path = kind["api_endpoint"]
        url = self.folio_client.okapi_url + path
        if kind["total_records"]:
            payload = {"records": list(batch), "totalRecords": len(batch)}
        else:
            payload = {kind["object_name"]: batch}
        return requests.post(
            url, data=json.dumps(payload), headers=self.folio_client.okapi_headers
        )

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "objects_file", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(parser, "batch_size", "batch size", "")
        ServiceTaskBase.add_argument(parser, "results_folder", "Folder where failing records "
                                                               "and logs will be stored", "DirChooser")
        ServiceTaskBase.add_argument(parser, "object_name", "What objects to batch post", "Dropdown",
                                     choices=list(list_objects().keys()),
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "objects_file", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "batch_size", "batch size")
        ServiceTaskBase.add_cli_argument(parser, "results_folder", "Folder where failing records "
                                                                   "and logs will be stored")
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


def get_human_readable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', "TB"]
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])


def get_req_size(response):
    size = response.request.method
    size += response.request.url
    size += '\r\n'.join('{}{}'.format(k, v) for k, v in response.request.headers.items())
    size += response.request.body if response.request.body else []
    return get_human_readable(len(size.encode('utf-8')))
