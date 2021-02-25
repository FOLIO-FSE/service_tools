import json
import os
import uuid

from folioclient import FolioClient

from acquisitions_migration.order_migration_base import OrderMigrationBase
from service_tasks.service_task_base import ServiceTaskBase


class MigratePurchaseOrdersVoyager(ServiceTaskBase, OrderMigrationBase):
    def __init__(self, args):
        print(args)
        self.millennium_items_path = args.data_path
        self.result_file = os.path.join(args.result_path, "po_lines.json")
        super().__init__(folio_client)

    @staticmethod
    def add_arguments(parser):
        # XLSX spreadsheet
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "data_path", "Path to the file", "FileChooser")
        ServiceTaskBase.add_argument(parser, "result_path", "Path to the file", "DirChooser")

    @staticmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "data_path", help="path to source file")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="path to results file")

    def do_work(self):
        new_order = self.instantiate_purchase_order(str(uuid.uuid4()))
        print(json.dumps(new_order))
