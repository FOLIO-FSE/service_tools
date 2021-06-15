import pandas as pd
import csv
import json

from service_tasks.service_task_base import ServiceTaskBase

class IdentifyImpossibleLoans(ServiceTaskBase):
    # Open file and read into a Pandas Dataframe
    def __init__(self, args):
        super().__init__()
        print("\n~*~*~\nLet's get started!")
        self.loan_file = args.loan_file
        self.item_file = args.item_file
        self.user_file = args.user_file

        self.good_file = f"{args.save_to_folder}/good_loans.tsv"
        self.bad_file = f"{args.save_to_folder}/bad_loans.tsv"
        self.bad_report = f"{args.save_to_folder}/bad_loans_report.txt"

        self.processed = 0

    def do_work(self):
        with open(self.loan_file, encoding='utf-8-sig') as loan_file, open(self.item_file) as item_file, open(self.user_file) as user_file:

            # Fetch data from items and user file
            items = {}
            for row in item_file:
                item = json.loads(row)
                item_barcode = item.get("barcode")
                item_status = item["status"]["name"]
                items[item_barcode] = item_status

            users = []
            for row in user_file:
                user = json.loads(row)
                users.append(user.get("barcode"))

            # Read loans file
            try:
                if self.loan_file.endswith(".csv"):
                    loans = csv.DictReader(loan_file)
                elif self.loan_file.endswith(".tsv"):
                    loans = csv.DictReader(loan_file, delimiter="\t")
                else:
                    print("Please supply a loan file with file extension .csv or .tsv")
                    raise Exception
            except:
                raise

            good_loans = []
            bad_loans = []
            bad_loan_report = []
            no_user_no_item = 0
            no_user = 0
            no_item = 0
            bad_status = {}

            for loan in loans:
                try:
                    print(loan)
                    loan_user_barcode = loan["patron_barcode"]
                    loan_item_barcode = loan["item_barcode"]
                    if loan_user_barcode not in users and loan_item_barcode not in items:
                        bad_loan_report.append(f"Neither user nor item for loan:\t{loan}")
                        bad_loans.append(loan)
                        no_user_no_item += 1
                    elif loan_user_barcode not in users:
                        bad_loan_report.append(f"No user for loan:\t{loan}")
                        bad_loans.append(loan)
                        no_user += 1
                    elif loan_item_barcode not in items:
                        bad_loan_report.append(f"No item for loan:\t{loan}")
                        bad_loans.append(loan)
                        no_item += 1
                    elif items[loan_item_barcode] != "Available":
                        bad_loan_report.append(f"Loan with status\t\"{items[loan_item_barcode]}\" cannot be checked out:\t{loan}")
                        bad_loans.append(loan)
                        if items[loan_item_barcode] in bad_status:
                            bad_status[items[loan_item_barcode]] += 1
                        else:
                            bad_status[items[loan_item_barcode]] = 1
                    else:
                        good_loans.append(loan)
                except KeyError as e:
                    print(f"Does your data have the right headers? Missing {e}.")

            good_loans_df = pd.DataFrame(good_loans)
            bad_loans_df = pd.DataFrame(bad_loans)

            with open(self.good_file, "w") as good_file, open(self.bad_file, "w") as bad_file, open(self.bad_report, "w") as bad_report:
                good_loans_df.to_csv(good_file, sep="\t", index=False, line_terminator='\n')
                bad_loans_df.to_csv(bad_file, sep="\t", index=False, line_terminator='\n')
                print(*bad_loan_report, file=bad_report, sep="\n")

            print(f"Good loans: {len(good_loans)}")
            print(f"Bad loans total: {len(bad_loans)}")

            print(f"Loans with neither user nor item: {no_user_no_item}")
            print(f"Loans with no user: {no_user}")
            print(f"Loans with no item: {no_item}")
            print(f"Loans with non-loanable status: {bad_status}")




    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_argument(sub_parser,
                                     "loan_file",
                                     "A .tsv or .csv file",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "item_file",
                                     "A json file containing one object per row.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "user_file",
                                     "A json file containing one object per row.",
                                     "FileChooser"),
        ServiceTaskBase.add_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.",
                                     "DirChooser")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "loan_file",
                                     "A .tsv or .csv file"),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "item_file",
                                     "A json file containing one object per row."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "user_file",
                                     "A json file containing one object per row."),
        ServiceTaskBase.add_cli_argument(sub_parser,
                                     "save_to_folder",
                                     "Folder where you want the output to be saved.")