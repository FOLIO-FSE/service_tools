import json
import time
from abc import abstractmethod
from datetime import datetime
import urllib

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class PostAnyJsonRecords(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.objects_file_path = args.objects_file_path
        self.endpoint = args.endpoint
        self.dupe_check = args.dupe_check
        self.failed_posts = 0
        # Start timers
        self.start_date_time = datetime.now()
        self.start = time.time()
        self.num_records = 0
        self.num_posted = 0
        self.num_deduped = 0

    def do_work(self):
        print(
            f"Let's get started! Starting work on {self.objects_file_path}...")
        with open(self.objects_file_path, encoding="utf8") as f:
            records = json.load(f)
            for rec in records:
                rec_id = rec.get("id") if rec.get("id") else rec.get("name")

                if self.dupe_check == "yes":
                    is_dupe = self.check_for_rec_in_folio(rec_id)
                else:
                    is_dupe = False

                if not is_dupe:
                    try:
                        url = f"{self.folio_client.okapi_url}{self.endpoint}"
                        body = json.dumps(rec, ensure_ascii=False)
                        req = requests.post(
                            url, headers=self.folio_client.okapi_headers, data=body.encode('utf-8'))

                        if req.status_code == 201:
                            self.num_posted += 1
                        elif req.status_code == 422:
                            self.failed_posts += 1
                            print(
                                f"{rec_id}\tHTTP {req.status_code}\t Error: {json.loads(req.text)['errors'][0]['message']}\t{json.dumps(rec)}")
                        else:
                            self.failed_posts += 1
                            print(
                                f"HTTP {req.status_code}\tRecord: {rec}\t{req.text}"
                            )
                    except Exception as ee:
                        print(f"Errror in rec {rec} {ee}")
                        if self.num_posted > 10:
                            raise ee

                self.num_records += 1
                time.sleep(0.01)    

            if self.num_records % 10 == 0:
                print(
                    f"{round(self.num_records / (time.time() - self.start))} recs/s\t{self.num_records}", flush=True)

        print(f"Done! Posted {self.num_posted} recs out of {self.num_records} in file. Already in FOLIO, not posted: {self.num_deduped}. Failed: {self.failed_posts}")

    def check_for_rec_in_folio(self, rec_name):
        if self.endpoint == "/licenses/licenses" or self.endpoint == "/erm/sas":
            query = "?filters=" + urllib.parse.quote("name==" + rec_name)
            matched_record = self.folio_client.folio_get(self.endpoint, query=query)
            if len(matched_record) == 1:
                self.num_deduped += 1
                print(f"{rec_name} already in FOLIO. Not posting to avoid creating duplicates.")
                return True
            elif len(matched_record) > 1:
                print(f"More than one matches for {rec_name}!")
        elif self.endpoint == "/circulation/requests":
            try:
                path = self.endpoint + '/' + rec_name
                request = self.folio_client.folio_get(path)
                if request:
                    # print(f'found! {request["id"]}')
                    return True
                else:
                    #print("Not found!")
                    return False
            except Exception as ee:
                # print(ee)
                return False
        else:
            "Functionality for doing this for non licennse/agreement records not built out...."

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(
            parser, "objects_file_path", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(
            parser, "endpoint", "Endpoint to post the records to. Eg /organozations/organizations", "")
        ServiceTaskBase.add_argument(
            parser, "dupe_check", "Avoid creating agreement/license dupes by doing a GET before posting to check if a record with same 'name' value already exists.",  widget='Dropdown',
                                     choices=["no","yes"], default="no")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(
            parser, "objects_file_path", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "endpoint", "Endpoint to post the records to")
        ServiceTaskBase.add_cli_argument(
            parser, "dupe_check", "(no/yes) Avoid creating agreement/license dupes by doing a GET before posting to check if a record with same 'name' value already exists.", default="no")
