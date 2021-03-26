import itertools
import logging
import random
from abc import abstractmethod
from datetime import datetime, timedelta

from faker import Faker

from helpers.circulation_helper import CirculationHelper
from service_tasks.service_task_base import ServiceTaskBase


class GenerateFakeLoans(ServiceTaskBase):
    """Class that is responsible for the actual work"""

    def __init__(self, folio_client, args):
        super().__init__(folio_client)
        self.setup_logging(args.results_path)
        """Init, setup"""
        self.folio_client = folio_client
        self.faker = Faker()
        self.items = set()
        self.loan_policies = {}
        self.create_requests = True
        self.create_page_requests = True
        self.patron_groups = ["ba484dd9-a2c3-4d80-b067-91cd2066134b", "6ad290aa-5851-4356-bb8d-1015e40c05c2", "d01b7bba-48fb-4264-833b-b88d23505404","d010bfa2-4983-4741-9ef8-1295484297cc"]
        logging.info(f"{len(self.patron_groups)} patron groups")

        self.item_loan_types = ["e8b311a6-3b21-43f2-a269-dd9310cb2d0e", "2e48e713-17f3-4c13-a9f8-23845bb210a4", "2b94c631-fca9-4892-a730-03ee529ffe27"]
        logging.info(f"{len(self.item_loan_types)} item loan types")

        self.item_material_types = ["025ba2c5-5e96-4667-a677-8186463aee69", "b3d29557-c74d-403d-a279-a2ef6b3a80f6"]
        logging.info(f"{len(self.item_material_types)} item material types")

        self.service_points = ["3a7de149-f17d-4602-adfe-0b09bf8e884a"]
        logging.info(f"{len(self.service_points)} Service points")

        self.locations = ["23f6dc01-1d53-4dfa-8163-60bf1f5cc4cd", "dcd9815f-f66b-401c-a345-acc3e0d0acf4"]
        logging.info(f"{len(self.locations)} locations")

        self.item_seeds = list(
            itertools.product(
                self.item_material_types, self.item_loan_types, self.locations
            )
        )
        # Shuffle the list of combinations so that you can run multiple instances at the same time
        random.shuffle(self.item_seeds)
        logging.info(f"Created randomized list of {len(self.item_seeds)} possible combinations")
        logging.info("Init done.")

    def do_work(self):
        logging.info("Starting....")
        # Iterate over every combination
        for seed in self.item_seeds:
            material_type_id = seed[0]
            loan_type_id = seed[1]
            location_id = seed[2]
            i_query = f'?query=(materialTypeId="{material_type_id}" and ' \
                      f'permanentLoanTypeId="{loan_type_id}" and ' \
                      f'effectiveLocationId="{location_id}" and ' \
                      f'status.name=="Available")'
            # iterate over every patron group
            for patron_group_id in self.patron_groups:

                # get random Items from FOLIO based on the combination of parameters
                items = self.folio_client.get_random_objects(
                    "/item-storage/items", 10, query=i_query
                )

                # Get patrons from the current patron group
                p_query = f'query=(patronGroup=="{patron_group_id}" and active==true)'
                patrons = self.folio_client.get_random_objects("/users", 10, p_query)

                # tie a patron to an item
                item_patrons = zip(items, patrons)

                for item_patron in item_patrons:

                    # make sure we have barcodes
                    if "barcode" in item_patron[1] and "barcode" in item_patron[0]:

                        # pick a random service point
                        service_point_id = random.choice(self.service_points)
                        combo_failed = False
                        # 5 out of 6 items are checked out if argument -p was given
                        if random.randint(0, 5) > 0 or not self.create_page_requests:
                            # check out the item
                            checkout = CirculationHelper.check_out_by_barcode(self.folio_client,
                                                                              item_patron[0]["barcode"],
                                                                              item_patron[1]["barcode"],
                                                                              service_point_id
                                                                              )

                            # "extend" the loan date backwards in time in a randomized matter
                            if checkout[0]:
                                extension_date: datetime = self.faker.date_time_between(
                                    start_date="-1y", end_date="now"
                                )
                                extension_out_date = extension_date - timedelta(days=90)
                                CirculationHelper.extend_open_loan(
                                    self.folio_client,
                                    checkout[1], extension_date, extension_out_date
                                )

                        # 1 out of 6 items are paged if argument -p was given
                        else:
                            logging.info("create page request")
                            CirculationHelper.create_request(
                                self.folio_client,
                                "Page",
                                item_patron[1],
                                item_patron[0],
                                service_point_id,
                            )

                        # TODO: speed up this thingy. Fetching users is slow
                        # Create requests for the loan or page. If -r was given
                        if self.create_requests and not combo_failed:
                            for b in random.sample(range(30), random.randint(1, 4)):
                                # pick random patron
                                new_patron = next(
                                    iter(
                                        self.folio_client.get_random_objects(
                                            "/users", 1, p_query
                                        )
                                    )
                                )
                                # request the item
                                req_results = CirculationHelper.create_request(self.folio_client,
                                                                               random.choice(["Hold", "Recall"]),
                                                                               new_patron,
                                                                               item_patron[0],
                                                                               service_point_id,
                                                                               )
                                if not req_results:
                                    combo_failed = True
                                    logging.warn("Combination failed. No more trying to create requests")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_argument(parser, "results_path", "Path to results and logs", "DirChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
        ServiceTaskBase.add_cli_argument(parser, "results_path", "Path to results and logs")