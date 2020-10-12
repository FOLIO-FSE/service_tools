import json
import os
import traceback
from user_migration.mappers import *
import importlib

from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase
from user_migration.mappers.default import Default


def get_import_struct(batch):
    return {
        "source_type": "",
        "deactivateMissingUsers": False,
        "users": list(batch),
        "updateOnlyPresentFields": False,
        "totalRecords": len(batch),
    }


class MigrateUsers(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.failed_ids = []
        self.posted_records = 0
        self.failed_objects = []
        self.batch_size = int(args.batch_size)
        self.objects_file = args.objects_file
        self.results_path = os.path.join(args.results_folder, "users")
        self.transformer = Default(self.folio_client, args)

    def do_work(self):
        raise NotImplementedError("Create ID-Legacy ID Mapping file!")
        raise NotImplementedError("Check for ID duplicates (barcodes, externalsystemID:s, usernames, emails?, ")

        print("Starting....")
        batch = []
        i = 0
        try:
            with open(self.objects_file, encoding="utf8") as object_file:
                for legacy_user in self.transformer.get_users(object_file):
                    i += 1
                    try:
                        folio_user = self.transformer.do_map(legacy_user)
                        batch.append(folio_user)
                        if len(batch) == self.batch_size:
                            self.post_batch(batch)
                            self.write_results(batch, f"user_batch{i}.json")
                            batch = []
                        if i == 1:
                            print("## First user")
                            print(json.dumps(folio_user, indent=4, sort_keys=True))
                        self.add_stats("Successfull user transformations")
                    except ValueError as ve:
                        print(ve)
                    except Exception as ee:
                        print(i)
                        print(ee)
                        print(json.dumps(legacy_user))
                        traceback.print_exc()
                        self.add_stats("Failed user transformations")
                        raise ee
                print("Posting last batch...")
                self.post_batch(batch)
                self.write_results(batch, f"user_batch{i}.json")
        except Exception as ee:
            print(ee)
            print(i)
            traceback.print_exc()
        self.print_dict_to_md_table(self.stats)
        self.transformer.write_migration_report()
        self.transformer.print_mapping_report(i)

    def post_batch(self, batch):
        response = self.do_post(get_import_struct(batch))
        if response.status_code == 200:
            self.posted_records += len(batch)
            print(
                f"Posting successful! {self.posted_records} {response.elapsed.total_seconds()}s {len(batch)}",
                flush=True,
            )
        elif response.status_code == 422:
            print(f"{response.status_code}\t{response.text}")
            resp = json.loads(response.text)

            for error in resp["errors"]:
                print(json.dumps(error))

        elif response.status_code in [500, 413]:
            print(f"{response.status_code}\t{response.text}")
            self.failed_objects.extend(batch)
        else:
            raise Exception(f"UNHANDLED ERROR! HTTP {response.status_code}\t{response.text}")

    def write_results(self, batch, file_name):
        if not os.path.exists(self.results_path):
            os.makedirs(self.results_path)
        path = os.path.join(self.results_path, file_name)
        with open(path, "w+") as results_file:
            results_file.write(json.dumps(get_import_struct(batch), indent=4))

    def do_post(self, payload):
        path = "/user-import"
        url = self.folio_client.okapi_url + path
        return requests.post(
            url, data=json.dumps(payload), headers=self.folio_client.okapi_headers
        )

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "objects_file", "path data file", "FileChooser")
        ServiceTaskBase.add_argument(parser, "results_folder",
                                     "Folder where results are saved. The script will create a "
                                     "./users subfolder and add results to it.",
                                     "DirChooser")
        ServiceTaskBase.add_argument(parser, "batch_size",
                                     "The number of users in each batch that is saved to disk and posted to FOLIO", "")
        ServiceTaskBase.add_argument(parser, "temp_email",
                                     "Email address to give all users during testing. Leave empty at go-live",
                                     "")
        ServiceTaskBase.add_argument(parser, "transformer_name",
                                     "Choose a transformer. If unsure and starting with a new client, try the default",
                                     "Dropdown",
                                     metavar='What objects to batch post',
                                     dest='transformer_name',
                                     choices=list(get_transformers().keys()),
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "objects_file", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "results_folder",
                                         "Folder where results are saved. The script will create a "
                                         "./users subfolder and add results to it.")
        ServiceTaskBase.add_cli_argument(parser, "batch_size",
                                         "The number of users in each batch that is saved to disk and posted to FOLIO")
        ServiceTaskBase.add_cli_argument(parser, "temp_email",
                                         "Email address to give all users during testing. Leave empty at go-live")
        ServiceTaskBase.add_cli_argument(parser, "transformer_name",
                                         "Choose a transformer. If unsure and starting with a new client,"
                                         "try the default",
                                         choices=list(get_transformers().keys()))


def get_transformers():
    ret = {
        "default": {"transformer": "default"},
        "Alabama": {"parser": ""},
        "AlabamaBanner": {"parser": ""},
        "FiveColleges": {"parser": ""},
        "MSUMigration": {"parser": ""}
    }
    return ret


def chunks(records, number_of_chunks):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(records), number_of_chunks):
        yield records[i: i + number_of_chunks]
