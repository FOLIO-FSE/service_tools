import json
import logging
import os
import traceback
from abc import abstractmethod
from pathlib import Path
from typing import Dict

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase
from user_migration.mappers.default import Default


def get_import_struct(batch) -> Dict:
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

        # Properties
        self.failed_ids = []
        self.use_group_map = True
        self.results_path = None
        self.group_map_path = None
        self.failed_objects = []
        self.client_folder = Path(args.client_folder)
        self.data_files = None
        self.data_map_combos = []

        # Init stuff
        self.setup_folder_structures()

        self.transformer = Default(self.folio_client, args)
        """if not args.use_user_map and args.mapping_file_path:
            raise ValueError("You have a specified a user mapping file, but not checked the Use a map checkbox")"""

    def setup_folder_structures(self):
        # Client folder
        if self.client_folder.is_dir():
            logging.info(f"Client Folder is {self.client_folder}. Looking for folder structure")
        else:
            raise Exception(f"Client Folder supplied - {self.client_folder} - is not a folder")
        self.results_path = self.client_folder / "results"
        if self.results_path.is_dir():
            logging.info(f"Reports, maps etc will be stored at  {self.results_path}. ")
        else:
            raise Exception(f"Results folder supplied - {self.results_path} - is not a folder")

        # Mapping file folder and file
        parent = self.client_folder.parent
        parent_children = list(os.walk(parent))[0][1]
        p = next((f for f in list(parent_children) if f.startswith("migration_")), None)

        if not p or not (parent / p).is_dir():
            raise Exception(
                f"Could not find Git repository path next to the client folder in {parent}"
                "The folder should be named migration_")
        git_repo_path = (parent / p)
        mapping_path = (parent / p) / "mapping_files"
        if not mapping_path.is_dir():
            raise Exception(
                f"Could not find mapping_files folder path at {mapping_path} ")
        logging.info(f"Mapping file path found at {mapping_path}")
        group_map_path = mapping_path / 'user_groups.tsv'
        if not group_map_path.is_file():
            self.use_group_map = False
            logging.info(f"user_groups.tsv NOT found in {mapping_path}. Will try to match current group codes to FOLIO")
        else:
            logging.info(f"User group mapping found at {group_map_path}")
            self.group_map_path = group_map_path

        # objects files
        obj_folder = self.client_folder / 'data' / 'users'
        if not git_repo_path.is_dir():
            raise Exception(f"Could not find user data files path expected to be at {obj_folder}")
        self.data_files = list(obj_folder.glob('**/*'))
        if not self.data_files:
            raise Exception(
                f"Could not find any user files at {obj_folder} ")
        mapping_files = list(os.path.basename(f) for f in list(mapping_path.glob('**/*')) if f.is_file())
        for data_file in self.data_files:
            name_part = os.path.splitext(os.path.basename(data_file))[0]
            map_file = next((f for f in mapping_files if name_part in f), "")
            map_path = mapping_path / map_file
            if map_path.is_file() and data_file.is_file():
                self.data_map_combos.append({"data_file": data_file, "mapping_file": mapping_path / map_file})
        if not any(self.data_map_combos):
            raise Exception(f"No data and mapping file combinations found.\n"
                            f"Make sure you have your users file(s) in {obj_folder} "
                            f"and name them the same as the mapping files in {mapping_path}")
        else:
            logging.info(f"Found {len(self.data_map_combos)} data-mapping file combinations")
        logging.info("Done Checking folder structure")

    def do_work(self):
        logging.info("Starting....")
        i = 0
        try:
            with open(os.path.join(self.results_path, 'folio_users.json'), "w+") as results_file:
                for combo in self.data_map_combos:
                    i = 0
                    with open(combo["data_file"], encoding="utf8") as object_file, \
                            open(combo["mapping_file"], encoding="utf8") as mapping_file:
                        logging.info(f'processing {combo["data_file"]}')
                        user_map = json.load(mapping_file)
                        file_format = "tsv" if str(combo["data_file"]).endswith(".tsv") else "csv"
                        for legacy_user in self.transformer.get_users(object_file, file_format):
                            i += 1
                            try:
                                folio_user = self.transformer.do_map(legacy_user, user_map)
                                clean_user(folio_user)
                                results_file.write(f"{json.dumps(folio_user)}\n")
                                if i == 1:
                                    print("## First Legacy  user")
                                    print(json.dumps(legacy_user, indent=4))
                                    print("## First FOLIO  user")
                                    print(json.dumps(folio_user, indent=4, sort_keys=True))
                                self.add_stats("Successful user transformations")
                                if i % 1000 == 0:
                                    logging.info(f"{i} users processed")
                            except ValueError as ve:
                                logging.error(ve)
                            except Exception as ee:
                                logging.error(i)
                                logging.error(json.dumps(legacy_user))
                                self.add_stats("Failed user transformations")
                                raise ee
        except Exception as ee:
            logging.error(i, exc_info=True)
        self.print_dict_to_md_table(self.stats)
        self.transformer.write_migration_report()
        self.transformer.print_mapping_report(i)

    def wrap_up(self):
        path = os.path.join(self.results_path, "user_id_map.json")
        logging.info("Saving map of {} old and new IDs to {}".format(len(self.transformer.legacy_id_map), path))
        with open(path, "w+") as id_map_file:
            json.dump(self.transformer.legacy_id_map, id_map_file, indent=4)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "client_folder",
                                     "Folder where results are saved. The script will create a "
                                     "./users sub folder and add results to it.",
                                     "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "client_folder",
                                         "Client folder for current migration. Assumes a certain folder structure.")


def clean_user(folio_user):
    del folio_user["id"]
    for address in folio_user.get("personal", {}).get("addresses", []):
        del address["id"]
