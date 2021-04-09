from abc import abstractmethod
import sqlparse

from service_tasks.service_task_base import ServiceTaskBase
from sql_queries.sql_queries import sql_queries


class SQLLibrary(ServiceTaskBase):
    def __init__(self, args):
        self.query_name = args.query_name
        self.tenant_id = args.tenant_id

    def do_work(self):
        current = next(f for f in sql_queries if self.query_name == f["name"])
        print(sqlparse.format(current["query"], reindent=True, keyword_case='upper').format(tenant_id=self.tenant_id))

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "query_name", "What objects to batch post", "Dropdown",
                                     choices=list(get_names()),
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "tenant_id",
                                     "Tenant ID", ""
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "query_name", "What objects to batch post",
                                         choices=list(get_names())
                                         )
        ServiceTaskBase.add_cli_argument(parser,
                                         "tenant_id",
                                         "Tenant ID")


def get_names():
    return list(q["name"] for q in sql_queries)
