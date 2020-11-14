from service_tasks.service_task_base import ServiceTaskBase

class ListRecallsWithAvailableItems(ServiceTaskBase):
    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        print("init")
        self.ui_url = args.ui_url
        print(folio_client.okapi_token)


    # Define a function that makes a GET request with a query
    def make_get_request_w_query_and_limit(self, endpoint, query, records):
        request_url = f"{self.folio_client.okapi_url}{endpoint}"

        # Make a GET request. Not sure correctly formatted for folio_client... eg where to put the limit parameter?
        response = self.folio_client.folio_get_all(request_url, records, query)
        # As I understand I get the list of returned records back. Errors already handled?
        return response

    def do_work(self):
        # Start recall stat counters
        has_available_items = 0
        no_available_items = 0

        recalls_to_move = []

        # Fetch all open recall requests

        recalls = make_get_request_w_query_and_limit(
            "circulation/requests",
            "requestType==\"Recall\" AND status==\"Open - Not yet filled\"",
            500, "requests")

        # Loop through fetched recall requests
        for recall in recalls:
            request_date = recall["requestDate"]
            linked_instance = recall["item"]["instanceId"]
            title = recall["item"]["title"]

            # Fetch items associated with the instance that are available and loanable
            available_items = make_get_request_w_query_and_limit(
                "inventory/items",
                f"instance.id=={linked_instance} AND status.name==\"Available\" AND permanentLoanTypeId==\"11fbed26-571e-40fb-9e26-80605602021d\"",
                100, "items"
            )

            # If there are any items available and loanable, add the recall request to list recalls_to_move
            if available_items:
                recall_id = recall["id"]
                recall_url = self.ui_url + f"/requests/view/{recall_id}"
                requester = recall["requester"]["lastName"]

                recall_info = f"{linked_instance}    {recall_url}    ({request_date} {requester})    {title}"

                recalls_to_move.append(recall_info)
                has_available_items += 1

            else:
                no_available_items += 1

        # Wrapping up... print summary to console
        print(
            f"Number of recalls with available items: {has_available_items}"
        )
        print(
            f"Number of recalls with no available items: {no_available_items}"
        )

        # Print results and list of recalls to move to a file in directory results. If a file by the name already exists, it will be overwritten.

        sorted_recalls_to_move = sorted(recalls_to_move)

        with open("results/recalls_to_move.txt", "w") as f:
            # TODO Get time from service tasks
            # print(f"This search was inititalized on: {start_date_time}", file=f)
            print(f"Number of recalls with available items: {has_available_items}", file=f)
            print(f"Number of recalls with no available items: {no_available_items}", file=f)
            print(f"\nRecalls that can be moved to available items:", file=f)
            print(*sorted_recalls_to_move, sep="\n", file=f)


    @staticmethod
    def add_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_argument(sub_parser,
                                     "ui_url",
                                     "The UI URL to the FOLIO environment, to be used in librarian-friendly output", "")


    @staticmethod
    def add_cli_arguments(sub_parser):
        ServiceTaskBase.add_common_arguments(sub_parser)
        ServiceTaskBase.add_cli_argument(sub_parser,
                                         "ui_url",
                                         "The UI URL to the FOLIO environment, to be used in librarian-friendly output")
