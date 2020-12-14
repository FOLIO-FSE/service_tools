import time
from datetime import datetime
from service_tasks.service_task_base import ServiceTaskBase


class ListRecallsWithAvailableItems(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("Let's go!")
        self.ui_url = args.ui_url
        self.loan_type = args.loan_type
        self.outfile = args.results_file_path

        # Start timers
        self.start_date_time = datetime.now()
        self.start = time.time()
        self.num_records = 0

        # Start recall stat counters
        self.has_available_items = 0
        self.no_available_items = 0
        self.recalls_to_move = []

    def do_work(self):
        # Fetch all open recall requests
        recalls = self.folio_client.folio_get_all("/circulation/requests", "requests", "?query=(requestType==\"Recall\" AND status==\"Open - Not yet filled\")")

        # Loop through fetched recall requests
        for recall in recalls:
            request_date = recall["requestDate"]
            linked_instance = recall["item"]["instanceId"]
            title = recall["item"]["title"]

            # Fetch items associated with the instance that are available and loanable
            available_items = self.folio_client.folio_get("/inventory/items", query=f"?query=(instance.id=={linked_instance} AND status.name==\"Available\" AND permanentLoanTypeId==\"{self.loan_type}\")&limit=0")

            # If there are any items available and loanable, add the recall request to list recalls_to_move
            if available_items.get("totalRecords") > 0:
                recall_id = recall["id"]
                recall_url = self.ui_url + f"/requests/view/{recall_id}"
                requester = recall["requester"]["lastName"]

                recall_info = f"{linked_instance}    {recall_url}    ({request_date} {requester})    {title}"

                self.recalls_to_move.append(recall_info)
                self.has_available_items += 1

            else:
                self.no_available_items += 1

            # TODO Check if FOLIO client does this
            self.num_records += 1
            if self.num_records % 10 == 0:
                print(f"{round(self.num_records / (time.time() - self.start))} recs/s\t{self.num_records}", flush=True)

            # TODO Check if FOLIO client does this
            time.sleep(0.01)

        # Wrapping up... print summary to console
        print(
            f"Number of recalls with available items: {self.has_available_items}"
        )
        print(
            f"Number of recalls with no available items: {self.no_available_items}"
        )

        # Print results and list of recalls to move to a file in directory results. If a file by the name already exists, it will be overwritten.

        with open(self.outfile, "w") as f:
            print(f"This search was initialized on: {self.start_date_time}", file=f)
            print(f"Number of recalls with available items: {self.has_available_items}", file=f)
            print(f"Number of recalls with no available items: {self.no_available_items}", file=f)
            print(f"\nRecalls that can be moved to available items:", file=f)
            print(*sorted(self.recalls_to_move), sep="\n", file=f)


    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        
        ServiceTaskBase.add_argument(sub_parser,
                                     "ui_url",
                                     "The UI URL to the FOLIO environment, to be used in librarian-friendly output", "")
        # TODO Think about how to let the user input a list of loan types to include (or exclude) in the search for available items -- but also about how to avoid request too long error if the list is very long
        ServiceTaskBase.add_argument(sub_parser,
                                     "loan_type",
                                     "UUID of a loanable loan type (TODO: list of loan types)", "")
        ServiceTaskBase.add_argument(sub_parser,
                                     "results_file_path",
                                     "Where do you want to save the file with requests to move? E.g. C:/MyFolder/results.txt (N.B. If you select an existing file, contents will be over-written.)", "FileChooser")

    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "ui_url",
                                         "The UI URL to the FOLIO environment, to be used in librarian-friendly output")
        # TODO Think about how to let the user input a list of loan types to include (or exclude) in the search for available items -- but also about how to avoid request too long error if the list is very long
        ServiceTaskBase.add_argument(sub_parser,
                                     "loan_type",
                                     "UUID of a loanable loan type (TODO: list of loan types)")
        ServiceTaskBase.add__cli_argument(sub_parser,
                                     "results_file_path",
                                     "Where do you want to save the file with Recalls to move? E.g. C:/MyFolder/results.txt (N.B. If you select an existing file, contents will be over-written.")
