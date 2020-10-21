import time
import traceback
from abc import abstractmethod

from os import listdir
from os.path import isfile, join

from pymarc import MARCReader

from service_tasks.service_task_base import ServiceTaskBase


class MARCChecker(ServiceTaskBase):
    def __init__(self, args):
        self.marc_file_paths = args.marc_files.split(',')
        print(self.marc_file_paths)
        print("Init done")

    def do_work(self):
        start = time.time()
        failed_files = []
        """files = [
            join(self.marc_file_path, f)
            for f in listdir(self.marc_file_path)
            if isfile(join(self.marc_file_path, f))
        ]"""

        print("Files to process: {}".format(len(self.marc_file_paths)))
        i = 0
        failed = 0
        for file_name in self.marc_file_paths:
            print(f"processing {file_name}", flush=True)
            try:
                with open(file_name, "rb") as marc_file:
                    reader = MARCReader(marc_file, "rb", hide_utf8_warnings=False, permissive=False)
                    for idx, marc_record in enumerate(reader):
                        i += 1
                        if i % 1000 == 0:
                            elapsed = i / (time.time() - start)
                            elapsed_formatted = "{0:.2f}".format(elapsed)
                            print(
                                f"{elapsed_formatted} recs/sec Number of records: {i}, Failed: {failed}",
                                flush=True,
                            )
            except UnicodeDecodeError as decode_error:
                failed += 1
                print(
                    f"UnicodeDecodeError in {file_name} for index {idx} (after record id {marc_record['001'].data}) {decode_error}",
                    flush=True,
                )
                failed_files.append(file_name)
            except Exception as exception:
                failed += 1
                print(exception)
                traceback.print_exc()
                print(file_name)

        print(failed_files)

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "marc_files", help="Path to the file", widget="MultiFileChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "marc_files", help="Path to the file")
