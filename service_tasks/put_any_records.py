import json
import time
from abc import abstractmethod
from datetime import datetime
import urllib

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class PutAnyJsonRecords(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.objects_file_path = args.objects_file_path
        self.endpoint = args.endpoint
        self.failed_puts = 0
        # Start timers
        self.start_date_time = datetime.now()
        self.start = time.time()
        self.num_records = 0
        self.num_put = 0

    def do_work(self):
        print(
            f"Let's get started! Starting work on {self.objects_file_path}...")
        with open(self.objects_file_path, encoding="utf8") as f:
            records = json.load(f)
            for rec in records:
                rec_id = rec.get("id")

                try:
                    url = f"{self.folio_client.okapi_url}{self.endpoint}/{rec_id}"
                    body = json.dumps(rec, ensure_ascii=False)
                    req = requests.put(
                        url, headers=self.folio_client.okapi_headers, data=body.encode('utf-8'))

                    if req.status_code == 200:
                        self.num_put += 1
                    elif req.status_code == 422:
                        self.failed_puts += 1
                        print(
                            f"{rec_id}\tHTTP {req.status_code}\t Error: {req.text}")
                    else:
                        self.failed_puts += 1
                        print(
                            f"HTTP {req.status_code}\tRecord: {rec}\t{req.text}"
                        )
                except Exception as ee:
                    print(f"Errror in rec {rec} {ee}")
                    if self.num_put > 10:
                        raise ee

                self.num_records += 1
                time.sleep(0.01)    

            if self.num_records % 10 == 0:
                print(
                    f"{round(self.num_records / (time.time() - self.start))} recs/s\t{self.num_records}", flush=True)

        print(f"Done! Put {self.num_put} recs out of {self.num_records} in file. Failed: {self.failed_puts}")


    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(
            parser, "objects_file_path", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(
            parser, "endpoint", "Endpoint to post the records to. Eg /organozations/organizations", "")
       
    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(
            parser, "objects_file_path", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "endpoint", "Endpoint to post the records to")