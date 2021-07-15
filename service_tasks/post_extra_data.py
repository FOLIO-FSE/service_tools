import json
import csv
import logging
from abc import abstractmethod
import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class PostExtraMigrationData(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        # Get arguments and more
        self.data_file = args.data_file_path
        self.results_folder = args.results_folder_path
        self.failed_recs_path = self.results_folder + "\\failed_records.extradata"
        self.setup_logging(f"posting_extradata", self.results_folder)

        # Initiate counters
        self.num_processed = 0
        self.num_posted = 0
        self.num_failed = 0
        self.num_dupes = 0
        self.failed_rows = []

    def do_work(self):
        logging.info(
            f"Let's get started! Starting work on {self.data_file}...")
        with open(self.data_file, encoding="utf8") as data_file:
            extra_data = csv.reader(data_file, delimiter="\t")
            for i, row in enumerate(extra_data):
                self.num_processed += 1

                object_name = row[0]
                record = json.loads(row[1])
                
                try:
                    endpoint = self.get_object_endpoint(object_name)
                    url = f"{self.folio_client.okapi_url}/{endpoint}"
                    body = json.dumps(record, ensure_ascii=False)
                    response = self.post_objects(url, body)
                    # Interpret the response and deal with failed rows
                    if response.status_code == 201:
                        self.num_posted += 1
                    elif response.status_code == 422:
                        self.num_failed += 1
                        logging.error(
                            f"Row {i}\tHTTP {response.status_code}\t {json.loads(response.text)['errors'][0]['message']}")
                        if "id value already exists" not in json.loads(response.text)['errors'][0]['message']:
                            self.failed_rows.append(row[0] + "\t" + row[1])
                    else:
                        self.num_failed += 1
                        self.failed_rows.append(row[0] + "\t" + row[1])
                        logging.error(
                            f"Row {i}\tHTTP {response.status_code}\t {response.text}")

                except KeyError as ke:
                    self.num_failed += 1
                    self.failed_rows.append(row[0] + "\t" + row[1])
                    logging.error(f"Row {i}\t Cannot POST as object type not in object_types dict: {ke}")
                
                if self.num_processed % 10 == 0:
                    logging.info(
                        f"Total processed: {self.num_processed} Total failed: {self.num_failed} "
                        f"in {response.elapsed.total_seconds()}s")

        # Wrap up
        logging.info(
            f"Done!"
            f"\nSuccessfully posted {self.num_posted} recs out of {self.num_processed} in file."
            f" Number of failed rows: {self.num_failed}. "
            f"\nFailed rows written to {self.failed_recs_path}"
        )
        with open(self.failed_recs_path, "w") as out:
            print(*self.failed_rows, file=out, sep="\n")
    

    def post_objects(self, url, body):
        response = requests.post(
            url, headers=self.folio_client.okapi_headers, data=body.encode('utf-8'))
        return response


    def get_object_endpoint(self, object_name):
        object_types = {
            "precedingSucceedingTitles": "preceding-succeeding-titles",
            "precedingTitles":  "preceding-succeeding-titles",
            "succeedingTitles": "preceding-succeeding-titles",
        }
        return object_types[object_name]


    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(
            parser, "data_file_path", "Path to data file", "FileChooser")
        ServiceTaskBase.add_argument(
            parser, "results_folder_path", "Path to results folder", "DirChooser")


    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(
            parser, "objects_file_path", "path to data file")
        ServiceTaskBase.add_cli_argument(parser, "results_folder_path", "path to results folder")
