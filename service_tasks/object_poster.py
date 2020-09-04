import json
import traceback
from abc import abstractmethod
import time

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class SingleObjectsPoster(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.skip = args.skip
        self.objects_file_path = args.objects_file_path
        self.object_kind = list_objects()[args.object_name]
        self.num_rows = 0
        self.failed_posts = 0
        self.t0 = time.time()

    def do_work(self):
        with open(self.objects_file_path) as objects_file:
            print("Starting....")
            for _ in range(int(self.skip)):
                next(objects_file)
                self.num_rows += 1
            for row in objects_file:
                self.num_rows += 1
                t0_function = time.time()
                try:
                    url = f"{self.folio_client.okapi_url}{self.object_kind['api_endpoint']}"
                    req = requests.post(
                        url, headers=self.folio_client.okapi_headers, data=row.split("\t")[-1])

                    if req.status_code == 201:
                        # print(f"{self.num_rows}\tHTTP {req.status_code}\tPOST {url}")
                        if self.num_rows%100 == 0:
                            print(timings(self.t0, t0_function, self.num_rows))
                    elif req.status_code == 422:
                        self.failed_posts += 1
                        print(
                            f"{self.num_rows}\tHTTP {req.status_code}\t"
                            f"{json.loads(req.text)['errors'][0]['message']}\tPOST {url}\t{row}"
                            f" {timings(self.t0, t0_function, self.num_rows)}"
                        )
                    else:
                        self.failed_posts += 1
                        print(
                            f"{self.num_rows}\tHTTP {req.status_code}\t{req.text}\tPOST {url}\t{row}"
                        )
                except Exception as ee:
                    print(f"Errror in row {self.num_rows} {ee}")
                    if self.num_rows < 10:
                        raise ee

            print(f"Done! {self.num_rows} rows in file. Failed: {self.failed_posts}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        parser.add_argument("objects_file_path", help="path data file", widget="FileChooser")
        parser.add_argument("skip", help="Number of records to skip")
        parser.add_argument(
            metavar='What objects to post',
            help='What objects to post',
            dest='object_name',
            widget="Dropdown",
            choices=list(list_objects().keys()),
        )


def timings(t0, t0func, num_objects):
    avg = num_objects / (time.time() - t0)
    elapsed = time.time() - t0
    elapsed_func = num_objects / (time.time() - t0func)
    return f"Objects processed: {num_objects}\tTotal elapsed: {elapsed}\tAverage per object: {avg:.2f}\tElapsed this time: {elapsed_func:.2f}"


def list_objects():
    return {
        "Source Records": {"object_name": "records", "api_endpoint": "/source-storage/records"}
    }
