from service_tasks.service_task_base import ServiceTaskBase


class GivePermission(ServiceTaskBase):
    def __init__(self,folio_client, args):
        super().__init__(folio_client)
        pass

    @staticmethod
    def add_arguments(sub_parser):
        pass

    @staticmethod
    def add_cli_arguments(sub_parser):
        # persmission name
        # userName or UUID
        pass

    def do_work(self):
        # persmission name
        # userName or UUID
        pass