import requests

from service_tasks.service_task_base import ServiceTaskBase


class ListUsersByPermission(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("init")
        self.permission_name = args.permission_name
        print(folio_client.okapi_token)

    def do_work(self):
        print("Work")
        by_name_path = f'/perms/permissions'
        url = f"{self.folio_client.okapi_url}{by_name_path}"
        resp = self.folio_client.folio_get_all(by_name_path,"permissions", f'?query=permissionName=={self.permission_name}')
        permission = next(r for r in resp)
        for user_id in permission["grantedTo"]:
            print(user_id)

    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_argument(sub_parser,
                                     "permission_name",
                                     "The name of the permission, not the display name", "")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "permission_name",
                                         "The name of the permission, not the display name")
