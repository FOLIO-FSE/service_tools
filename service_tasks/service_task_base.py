import logging
import logging.handlers
import os
from abc import abstractmethod
from argparse import ArgumentParser

from folioclient import FolioClient


class ServiceTaskBase:
    def __init__(self, folio_client: FolioClient = None):
        self.stats = {}
        self.migration_report = {}
        self.folio_client = folio_client
        self.setup_logging()

    @staticmethod
    def setup_logging(log_file_path=None):
        logger = logging.getLogger()
        formatter = logging.Formatter(
            '%(levelname)s\t%(message)s\t%(asctime)s')
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file_path:
            log_file = os.path.join(log_file_path, "service_task_log.log")
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=log_file, when='midnight', backupCount=30)
            # file_handler.addFilter(LevelFilter(0, 20))
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(file_handler)
        logger.info("Logging setup")

    def write_migration_report(self, report_file):

        for a in self.migration_report:
            report_file.write(f"   \n")
            report_file.write(f"## {a}    \n")
            report_file.write(
                f"<details><summary>Click to expand all {len(self.migration_report[a])} things</summary>     \n"
            )
            report_file.write(f"   \n")
            report_file.write(f"Measure | Count   \n")
            report_file.write(f"--- | ---:   \n")
            b = self.migration_report[a]
            sortedlist = [(k, b[k]) for k in sorted(b, key=as_str)]
            for b in sortedlist:
                report_file.write(f"{b[0]} | {b[1]}   \n")
            report_file.write("</details>   \n")

    def add_stats(self, measure_to_add):
        if measure_to_add not in self.stats:
            self.stats[measure_to_add] = 1
        else:
            self.stats[measure_to_add] += 1

    def wrap_up(self):
        self.print_stats()
        self.print_migration_report()

    @staticmethod
    def print_dict_to_md_table(my_dict, h1="", h2=""):
        d_sorted = {k: my_dict[k] for k in sorted(my_dict)}
        print(f"{h1} | {h2}")
        print("--- | ---:")
        for k, v in d_sorted.items():
            print(f"{k} | {v}")

    def print_stats(self):
        self.print_dict_to_md_table(self.stats, "Measure", "  #  ")

    def add_to_migration_report(self, header, message_string):
        if header not in self.migration_report:
            self.migration_report[header] = list()
        self.migration_report[header].append(message_string)

    def print_migration_report(self):
        for a in self.migration_report:
            logging.info(f"# {a}")
            for b in self.migration_report[a]:
                logging.info(b)

    @staticmethod
    @abstractmethod
    def add_arguments(sub_parser):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def add_cli_arguments(sub_parser):
        raise NotImplementedError

    @staticmethod
    def add_argument(parser, destination, help, widget, **kwargs):
        # logging.info(parser.__class__.__name__)
        # logging.info(destination)
        parser.add_argument(dest=destination, help=help, widget=widget, metavar=kwargs.get('metavar'),
                            choices=kwargs.get('choices'), gooey_options=kwargs.get('gooey_options'),
                            action=kwargs.get('action'))

    @staticmethod
    def add_cli_argument(parser: ArgumentParser, destination, help, **kwargs):
        parser.add_argument(dest=destination, help=help, **kwargs)

    @abstractmethod
    def do_work(self):
        raise NotImplementedError

    @staticmethod
    def add_common_arguments(parser):
        parser.add_argument(
            "okapi_credentials_string", help="Space delimited string containing "
                                             "OKAPI_URL, TENANT_ID,  USERNAME, PASSWORD in that order."
        )


def as_str(s):
    try:
        return str(s), ''
    except ValueError:
        return '', s


class LevelFilter(logging.Filter):
    def __init__(self, low, high):
        self._low = low
        self._high = high
        logging.Filter.__init__(self)

    def filter(self, record):
        if self._low <= record.levelno <= self._high:
            return True
        return False
