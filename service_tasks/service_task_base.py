from abc import abstractclassmethod, abstractmethod

from folioclient import FolioClient


class ServiceTaskBase():
    def __init__(self, folio_client: FolioClient=None):
        self.stats = {}
        self.migration_report = {}
        self.folio_client = folio_client

    def add_stats(self, measure_to_add):
        if measure_to_add not in self.stats:
            self.stats[measure_to_add] = 1
        else:
            self.stats[measure_to_add] += 1

    def add_to_migration_report(self, header, message_string):
        if header not in self.migration_report:
            self.migration_report[header] = list()
        self.migration_report[header].append(message_string)

    @staticmethod
    @abstractmethod
    def add_arguments(sub_parser):
        raise NotImplementedError

    @abstractmethod
    def do_work(self):
        raise NotImplementedError


def print_dict_to_md_table(my_dict, h1="", h2=""):
    d_sorted = {k: my_dict[k] for k in sorted(my_dict)}
    print(f"{h1} | {h2}")
    print("--- | ---:")
    for k, v in d_sorted.items():
        print(f"{k} | {v}")
