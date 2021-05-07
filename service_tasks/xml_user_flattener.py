import csv
import json
import logging
import os
from abc import abstractmethod

import xmltodict as xd

from service_tasks.service_task_base import ServiceTaskBase


def init_dict():
    return {
        "EMAIL": "",
        "PHONE_NUMBER": "",
        "MIDDLE_NAME": "",
        "LAST_NAME": "",
        "FIRST_NAME": "",
        "ZIP_POSTAL": "",
        "STATE": "",
        "COUNTRY": "",
        "CITY": "",
        "ADDRESS_TYPE": "",
        "ADDRESS_LINE2": "",
        "ADDRESS_LINE1": "",
        "PATRON_GROUP_NAME": "",
        "Active": "",
        "EXPIRE_DATE": "",
        "INSTITUTION_ID": "",
        "USERNAME": ""}


class XMLUserFlattener(ServiceTaskBase):
    def __init__(self, args):
        self.source_path = args.data_path
        self.result_file = os.path.join(args.result_path, "flattenedusersfromVoyager.tsv")
        self.errors = 0

    def do_work(self):
        print("Let's get started!")

        with open(self.source_path, "rb") as source_file, open(self.result_file, 'w+') as results_file:
            writer = csv.DictWriter(results_file, fieldnames=init_dict().keys(), delimiter='\t', lineterminator="\n")
            d = xd.parse(source_file)
            for idx, patron in enumerate(d["patronList"]["patron"]):
                if idx == 0:
                    writer.writeheader()
                try:
                    res_patron = init_dict()
                    patron_email = patron.get("emailList", {})
                    if isinstance(patron_email.get("patronEmail", {}), list):
                        res_patron["EMAIL"] = patron_email.get("patronEmail", [])[0].get("email", "")
                    else:
                        res_patron["EMAIL"] = patron_email.get("patronEmail", {}).get("email", "")
                    res_patron["PHONE_NUMBER"] = patron.get("permAddress", {}).get("patronPhoneList", {}).get(
                        "patronPhone",
                        {}).get("phone","")
                    res_patron["MIDDLE_NAME"] = patron.get("middleName", "")
                    res_patron["LAST_NAME"] = patron.get("lastName", "")
                    res_patron["FIRST_NAME"] = patron.get("firstName", "")
                    res_patron["ZIP_POSTAL"] = patron.get("permAddress", {}).get("postalCode", "")
                    res_patron["STATE"] = patron.get("permAddress", {}).get("stateProvince", "")
                    res_patron["COUNTRY"] = patron.get("permAddress", {}).get("country", "")
                    res_patron["CITY"] = patron.get("permAddress", {}).get("city", "")
                    res_patron["ADDRESS_TYPE"] = patron.get("permAddress", {}).get("", "")
                    res_patron["ADDRESS_LINE2"] = patron.get("permAddress", {}).get("line2", "")
                    res_patron["ADDRESS_LINE1"] = patron.get("permAddress", {}).get("line1", "")
                    res_patron["USERNAME"] = res_patron["EMAIL"].split('@')[0]

                    barcode_list = patron.get("patronBarcodeList", {})
                    if isinstance(barcode_list.get("patronBarcode", {}), list):
                        res_patron["PATRON_GROUP_NAME"] = barcode_list.get("patronBarcode", [])[0].get("patronGroup",
                                                                                                       "")
                        res_patron["Active"] = barcode_list.get("patronBarcode", [])[0].get("barcodeStatus", "")
                    else:
                        res_patron["PATRON_GROUP_NAME"] = barcode_list.get("patronBarcode", {}).get("patronGroup", "")
                        res_patron["Active"] = barcode_list.get("patronBarcode", {}).get("barcodeStatus", "")
                    res_patron["EXPIRE_DATE"] = patron.get("expirationDate", "")
                    res_patron["INSTITUTION_ID"] = patron.get("institutionID", "")
                    writer.writerow(res_patron)
                    if idx % 1000 == 0:
                        print(json.dumps(res_patron, indent=4))
                        print(json.dumps(patron, indent=4))
                except:
                    logging.exception(f"Error in XML patron element number {idx}")
                    self.errors += 1
            print(f"Errors: {self.errors} out of {idx}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser,
                                     "data_path", "Path to the delimited file.", "FileChooser"
                                     )
        ServiceTaskBase.add_argument(parser,
                                     "result_path", "Folder where results will be saved", "DirChooser"
                                     )

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser,
                                         "data_path", help="Path to the delimited file.")
        ServiceTaskBase.add_cli_argument(parser, "result_path", help="Folder where results will be saved")
