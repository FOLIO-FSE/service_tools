from service_tasks.service_task_base import ServiceTaskBase, abstractmethod


class A0_ClearConsole(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    def do_work(self):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        pass

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        pass
