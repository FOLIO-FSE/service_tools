import argparse
import pathlib
import json
import requests
import datetime
from folioclient.FolioClient import FolioClient
import uuid
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class RefDataBackupDeleteAndLoad(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.action = args.action
        self.path = args.path
        self.ref_data_sets = get_sets()
        self.ref_data_set = self.ref_data_sets.get(args.ref_data_set, {})
        self.ref_data_set["name"] = args.ref_data_set

    def do_work(self):
        print(f"Performing {self.action} of {self.ref_data_set}")
        if self.action == "backup":
            print("Backup")
            backup = Backup(self.folio_client, self.path, self.ref_data_set)
            backup.backup()
        if self.action == "restore":
            print("Restore")
            restore = Restore(self.folio_client, self.path, self.ref_data_set)
            restore.restore()
        if self.action == "purge":
            print("purge")
            purge = Purge(self.folio_client, self.path, self.ref_data_set)
            purge.purge()

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "path",
                                     "Source or results folder depending on action",
                                     "DirChooser")
        ServiceTaskBase.add_argument(parser, "ref_data_set",
                                     "Choose a ref data set",
                                     "Dropdown",
                                     choices=get_sets().keys()
                                     )

        ServiceTaskBase.add_argument(parser, "action",
                                     "Which action to perform",
                                     "Dropdown",
                                     choices=["backup", "purge", "restore"]
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "path",
                                         "Source or results folder depending on action")
        ServiceTaskBase.add_cli_argument(parser, "ref_data_set",
                                         "Choose a ref data set",
                                         choices=get_sets().keys())
        ServiceTaskBase.add_cli_argument(parser, "action", "Which action to perform",
                                         choices=["backup", "purge", "restore"])


def get_sets():
    return {
        "all": {},
        "addressTypes": {
            "path": "/addresstypes",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "alternativeTitleTypes": {
            "path": "/alternative-title-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "callNumberTypes": {
            "path": "/call-number-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "cancellationReasons": {
            "path": "/cancellation-reason-storage/cancellation-reasons",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "categories": {
            "path": "/vendor-storage/categories",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "circulation_rules": {
            "path": "/circulation-rules-storage",
            "insertMethod": "put",
            "saveEntireResponse": True
        },
        "classificationTypes": {
            "path": "/classification-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "contributorNameTypes": {
            "path": "/contributor-name-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "contributorTypes": {
            "path": "/contributor-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "electronicAccessRelationships": {
            "path": "/electronic-access-relationships",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "fileExtensions": {
            "path": "/data-import/fileExtensions",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "holdingsTypes": {
            "path": "/holdings-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "identifierTypes": {
            "path": "/identifier-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "illPolicies": {
            "path": "/ill-policies",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "instanceFormats": {
            "path": "/instance-formats",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "instanceStatuses": {
            "path": "/instance-statuses",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "instanceTypes": {
            "path": "/instance-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "loanPolicies": {
            "path": "/loan-policy-storage/loan-policies",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "loantypes": {
            "path": "/loan-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "locations": {
            "path": "/locations",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "loccamps": {
            "path": "/location-units/campuses",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "locinsts": {
            "path": "/location-units/institutions",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "loclibs": {
            "path": "/location-units/libraries",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "mtypes": {
            "path": "/material-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "openingPeriods": {
            "path": "/calendar/periods",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "organizations": {
            "path": "/organizations-storage/organizations",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "patronNoticePolicies": {
            "path": "/patron-notice-policy-storage/patron-notice-policies",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "refunds": {
            "path": "/refunds",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "requestPolicies": {
            "path": "/request-policy-storage/request-policies",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "servicepoints": {
            "path": "/service-points",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "staffSlips": {
            "path": "/staff-slips-storage/staff-slips",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "statisticalCodeTypes": {
            "path": "/statistical-code-types",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "statisticalCodes": {
            "path": "/statistical-codes",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "tags": {
            "path": "/tags",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "templates": {
            "path": "/templates",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "usergroups": {
            "path": "/groups",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "users": {
            "path": "/users",
            "insertMethod": "post",
            "saveEntireResponse": False
        },
        "waiver": {
            "path": "/waives",
            "insertMethod": "post",
            "saveEntireResponse": False
        }
    }


class Purge:
    def __init__(self, folio_client, path, set):
        self.folio_client = folio_client
        self.path = path
        self.set = set
        print("initializing Purge")

    def purge(self):
        if self.set:
            print("purge setting {}".format(self.set))
            self.purge_one_setting(self.set)
        else:
            raise Exception("No setting provided. Halting...")

    def purge_one_setting(self, config):
        print(config)
        save_entire_respones = config["saveEntireResponse"]
        query = ("queryString" in config and config["queryString"]) or ""
        query = (
            query.replace("NNNOW", datetime.datetime.now().isoformat())
            if query
            else query
        )
        url = self.folio_client.okapi_url + config["path"]
        print("Fetching from: {}".format(url))
        page_size = 100
        req = self.make_request(url, 0, page_size, query)
        j = json.loads(req.text)
        total_recs = int(j["totalRecords"])
        res = list(self.parse_result(j, save_entire_respones, config))
        if total_recs > page_size and not save_entire_respones:
            my_range = list(range(page_size, total_recs, page_size))
            for offset in my_range:
                resp = self.make_request(url, offset, page_size, query)
                k = json.loads(resp.text)
                ll = self.parse_result(k, save_entire_respones, config)
                res.extend(ll)
        print(f"records to purge {len(res)}", flush=True)
        for i in res:
            try:
                ident = i["id"] if "id" in i else i["recordId"]
                url = self.folio_client.okapi_url + config["path"] + "/" + ident
                print(url, flush=True)
                headers = self.folio_client.okapi_headers
                req = requests.delete(url, headers=headers)
                print(req.status_code, flush=True)
                if not str(req.status_code).startswith("2"):
                    print(req.text, flush=True)
                    print(json.dumps(req.json), flush=True)
            except Exception as ee:
                print("ERROR=================================", flush=True)
                print(ee, flush=True)

    def parse_result(self, json, save_entire_response, config):
        if save_entire_response:
            return json
        elif config["name"] in json:
            return json[config["name"]]
        elif "data" in json:
            return json["data"]
        print("no parsing of response", flush=True)

    def make_request(self, path, start, length, query=""):
        paging_q = f"limit={length}&offset={start}"
        new_query = "?" + paging_q if not query else query + "&" + paging_q
        print(f"PATH: {path + new_query}")
        req = requests.get(path + new_query, headers=self.folio_client.okapi_headers)
        if req.status_code != 200:
            print(req.text, flush=True)
            raise ValueError("Request failed {}".format(req.status_code))
        return req


class Backup:
    def __init__(self, folio_client, path, set):
        self.folio_client = folio_client
        self.path = path
        self.set = set
        print("initializing Backup", flush=True)

    def load_schema(self, schema_location):
        req = requests.get(schema_location)
        return json.loads(req.text)

    def make_request(self, path, start, length, query=""):
        paging_q = f"limit={length}&offset={start}"
        new_query = "?" + paging_q if not query else query + "&" + paging_q
        print(f"PATH: {path + new_query}")
        req = requests.get(path + new_query, headers=self.folio_client.okapi_headers)
        if req.status_code != 200:
            print(req.text, flush=True)
            raise ValueError("Request failed {}".format(req.status_code))
        return req

    def parse_result(self, json, save_entire_respones, config):
        if save_entire_respones:
            return json
        elif config["name"] in json:
            return json[config["name"]]
        elif "data" in json:
            return json["data"]
        print("no parsing of response")

    def backup(self):
        if self.set:
            print("saving setting {}".format(self.set))
            self.save_one_setting(self.set)
        """else:
            for setting in settings:
            kk    print("saving setting {}".format(setting["name"]))
                self.save_one_setting(setting)"""

    def save_one_setting(self, config):
        query = ("queryString" in config and config["queryString"]) or ""
        url = self.folio_client.okapi_url + config["path"]
        print("Fetching from: {}".format(url))
        try:
            save_entire_respones = config["saveEntireResponse"]
            print(config)
            page_size = 1000
            req = self.make_request(url, 0, page_size, query)
            j = json.loads(req.text)
            total_recs = int(j["totalRecords"])
            res = list(self.parse_result(j, save_entire_respones, config))
            if total_recs > page_size and not save_entire_respones:
                my_range = list(range(page_size, total_recs, page_size))
                for offset in my_range:
                    resp = self.make_request(url, offset, page_size, query)
                    k = json.loads(resp.text)
                    ll = self.parse_result(k, save_entire_respones, config)
                    res.extend(ll)
            print(f"found {len(res)} records. Saving...")
            if len(res) > 0:
                setting = {"name": config["name"], "data": res}
                filename = config["name"] + ".json"
                path = pathlib.Path.cwd() / self.path / filename
                print("Saving to: {}".format(path))
                with pathlib.Path.open(path, "w+") as settings_file:
                    settings_file.write(json.dumps(setting))
            else:
                print("No data found")
        except Exception as ee:
            print("ERROR=========================={}".format(config["name"]))
            print(ee)


class Restore:
    def __init__(self, folio_client, path, set_name):
        self.folio_client = folio_client
        self.path = path
        self.set = set
        print("initializing Restore")

    def restore(self):
        if self.set:
            print("restoring setting {}".format(self.set))
            self.restore_one_setting(self.set)
        """else:
            for setting in settings:
                self.restore_one_setting(setting)"""

    def restore_one_setting(self, config):
        filename = config["name"] + ".json"
        path = pathlib.Path(self.path) / filename
        print("Path: {}".format(path))
        with pathlib.Path.open(path) as refdata_file:
            refdata = json.load(refdata_file)
            print("Restoring {}".format(config["name"]))
            for item in refdata["data"]:
                try:
                    url = self.folio_client.okapi_url + config["path"]
                    headers = self.folio_client.okapi_headers
                    if config["insertMethod"] == "put":
                        req = requests.put(url, data=json.dumps(item), headers=headers)
                        print(req.status_code)
                    if config["insertMethod"] == "post":
                        req = requests.putu(url, data=json.dumps(item), headers=headers)
                        print(req.status_code)
                        if str(req.status_code).startswith("4"):
                            print(req.text)
                            print(json.dumps(req.json))
                except Exception as ee:
                    print("ERROR=================================")
                    print(ee)
