import json
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class AddPermissionToUser(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client, self.__class__.__name__)
        self.username = args.username
        self.permission_name = args.permission_name

    def do_work(self):
        try:
            print(f"Adding {self.permission_name} to {self.username}")

            # get user uuid
            user_id_query = f'?query=(username=="{self.username}")'
            resp = list(self.folio_client.get_all('/users', "users", user_id_query))
            if not any(resp):
                raise ValueError(f"No user found with username {self.username}")
            user_uuid = resp[0]["id"]
            print(f"User UUID is {user_uuid}")

            # Get permissions user
            query = f'?query=(userId=="{user_uuid}")'
            resp = list(self.folio_client.get_all('/perms/users', "permissionUsers", query))
            if not any(resp):
                raise ValueError(f"No permissions user found with user id {user_uuid}")
            perms_user = resp[0]
            print(f"Permissions user {perms_user['id']} found with {len(perms_user['permissions'])} permissions")

            # Add the permission and put the user
            perms_user["permissions"].append(self.permission_name)
            resp = requests.put(f"{self.folio_client.okapi_url}/perms/users/{perms_user['id']}", data=json.dumps(perms_user),
                                headers=self.folio_client.okapi_headers)
            resp.raise_for_status()
            print(f"permission {self.permission_name} successfully added to user {self.username}")
            print(resp.status_code)
        except ValueError as value_error:
            print(value_error)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "permission_name", "name of the permission to add", "")
        ServiceTaskBase.add_argument(parser, "username", "user to look up", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "permission_name", "name of the permission to add")
        ServiceTaskBase.add_cli_argument(parser, "userid", "user to look up")
