import json
import os
import traceback
from typing import Dict

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
        self.post_users = True
        # self.post_users = args.post_users
        if self.post_users:
            print("Will post users to FOLIO and save them to disk")
        else:
            print("Will only post users to disk")
        self.transformer = Default(self.folio_client, args)
        """if not args.use_user_map and args.mapping_file_path:
            raise ValueError("You have a specified a user mapping file, but not checked the Use a map checkbox")"""

    def do_work(self):
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
                            if self.post_users:
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
                if self.post_users:
                    self.post_batch(batch)
                self.write_results(batch, f"user_batch{i}.json")
        except Exception as ee:
            print(ee)
            print(i)
            traceback.print_exc()
        self.print_dict_to_md_table(self.stats)
        self.transformer.write_migration_report()
        self.transformer.print_mapping_report(i)

    def wrap_up(self):
        path = os.path.join(self.results_path, "user_id_map.json")
        print("Saving map of {} old and new IDs to {}".format(len(self.legacy_id_map), path))
        with open(path, "w+") as id_map_file:
            json.dump(self.legacy_id_map, id_map_file, indent=4)

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
        ServiceTaskBase.add_argument(parser, "patron_group_map_path", "Location of the patron group mapping file",
                                     "FileChooser",required=False)
        ServiceTaskBase.add_argument(parser, "batch_size",
                                     "The number of users in each batch that is saved to disk and posted to FOLIO", "",
                                     gooey_options={'initial_value': '250'})
        """ServiceTaskBase.add_argument(parser, "post_users",
                                     "Post users to FOLIO. Default is to store them on disk",
                                     "BlockCheckbox", action="store_const")
        ServiceTaskBase.add_argument(parser, "use_user_map",
                                     "Use a user mapping file",
                                     "BlockCheckbox", action="store_const")"""
        ServiceTaskBase.add_argument(parser, "mapping_file_path", "Path to Map file", "FileChooser", required=False)
        ServiceTaskBase.add_argument(parser, "temp_email",
                                     "Email address to give all users during testing. Leave empty at go-live",
                                     "", required=False)

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "users_file", "path data file")
        ServiceTaskBase.add_cli_argument(parser, "results_folder",
                                         "Folder where results are saved. The script will create a "
                                         "./users subfolder and add results to it.")
        ServiceTaskBase.add_cli_argument(parser, "mappings_folder", "Location of mapping files, "
                                                                    "like patron group mappings.")

        ServiceTaskBase.add_cli_argument(parser, "batch_size",
                                         "The number of users in each batch that is saved to disk and posted to FOLIO")
        """ServiceTaskBase.add_cli_argument(parser, "post_users", "Post users to FOLIO. "
                                                               "Default is to store them on disk ",
                                         action="store_false")
        ServiceTaskBase.add_cli_argument(parser, "use_user_map", "Use a user mapping file",
                                         action="store_false")"""
        ServiceTaskBase.add_cli_argument(parser, "mapping_file_path", "Path to Map file. Leave empty if using a "
                                                                      "transformer other than Default")
        ServiceTaskBase.add_cli_argument(parser, "temp_email",
                                         "Email address to give all users during testing. Leave empty at go-live")


def chunks(records, number_of_chunks):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(records), number_of_chunks):
        yield records[i: i + number_of_chunks]
