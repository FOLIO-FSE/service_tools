import csv
import ctypes
import sys
from abc import abstractmethod

import pandas as pd

from service_tasks.service_task_base import ServiceTaskBase


class VoyagerTransactionsFeesCombinator(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.transactions_path = args.transactions_path
        self.fees_path = args.fees_path

    def do_work(self):
        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
        transactions = pd.read_csv(self.transactions_path, encoding = 'unicode_escape', engine ='python', sep='\t', header=0, dtype=str)
        fees = pd.read_csv(self.fees_path, encoding = 'unicode_escape', engine ='python', sep='\t', header=0, dtype=str)
        result = pd.merge(transactions, fees, on=["FINE_FEE_ID", "FINE_FEE_ID"])
        print(len(result.index))
        print(result["TRANS_TYPE"].value_counts())
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "transactions_path", "", "FileChooser")
        ServiceTaskBase.add_argument(parser, "fees_path", "", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "transactions_path", "")
        ServiceTaskBase.add_cli_argument(parser, "fees_path", "")
