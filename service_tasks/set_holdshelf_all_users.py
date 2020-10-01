import json
import traceback
from abc import abstractmethod
import requests

from service_tasks.service_task_base import ServiceTaskBase


class SetHoldShelfToAllUsers(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.reqpref_template = {
            "userId": "",
            "holdShelf": True,
            "delivery": False,
            "fulfillment": "Hold Shelf",
            "metadata": self.folio_client.get_metadata_construct()
        }

    def do_work(self):
        i = 0
        for user in self.folio_client.folio_get_all("/users", "users"):
            try:
                i += 1
                req_pref_path = f"/request-preference-storage/request-preference?query=(userId==\"{user['id']}\")"
                req_prefs = self.folio_client.folio_get(req_pref_path, "requestPreferences")
                if len(list(req_prefs)) > 0:
                    self.add_stats("Users with reqprefs")
                    print(f"DELETE {json.dumps(req_prefs[0])}")
                    requests.delete(f"{self.folio_client.okapi_url}/request-preference-storage/request-preference/{req_prefs[0]['id']}", headers=self.folio_client.okapi_headers)
                data_to_post = self.reqpref_template
                data_to_post['userId'] = user['id']
                print(f"POST! {user['id']}")
                post_url = f"{self.folio_client.okapi_url}/request-preference-storage/request-preference"
                resp = requests.post(post_url, data=json.dumps(data_to_post),
                                     headers=self.folio_client.okapi_headers)
                resp.raise_for_status()
                print(resp.status_code)
            except Exception as ee:
                print(ee)
                print(f'Failed! for user id {user["id"]}')
                traceback.print_exc()

        self.print_dict_to_md_table(self.stats)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
