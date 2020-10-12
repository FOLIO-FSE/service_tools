from abc import abstractmethod

from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class ListPermissions(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)
        self.user_id = args.userid

    def do_work(self):
        query = f'?query=(userId=="{self.user_id}")'
        resp = self.folio_client.get_all('/perms/users', "permissionUsers", query)
        print(resp[0]["id"])
        print("")
        print(f"# Permissions for {self.user_id} ")
        print("\n".join(resp[0]["permissions"]))

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser,"userid", "user to look up","")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "userid", "user to look up")