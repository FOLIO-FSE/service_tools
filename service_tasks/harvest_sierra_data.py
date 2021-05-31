import time, threading
import base64
import json
from abc import abstractmethod

import requests

from service_tasks.service_task_base import ServiceTaskBase


class HarvestSierraData(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        print("Init...")
        self.token_path = "/iii/sierra-api/token"
        self.base_uri = args.base_uri
        self.api_timeout_seconds = 2700
        self.encoded_credentials = to_base64(f"{args.public_key}:{args.private_key}")
        self.auth_token = ""
        self.authenticate()

    def do_work(self):
        print("Starting...")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "base_uri", "Base URI for Sierra API", "")
        ServiceTaskBase.add_argument(parser, "public_key", "Public Key for Sierra API", "")
        ServiceTaskBase.add_argument(parser, "private_key", "Private Key for Sierra API", "")
        ServiceTaskBase.add_argument(parser, "data_feed",
                                     "Choose a data feed/Pick ref data set",
                                     "Dropdown",
                                     choices=["apa"])

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "base_uri", "Base URI for Sierra API")
        ServiceTaskBase.add_cli_argument(parser, "public_key", "Public Key for Sierra API")
        ServiceTaskBase.add_cli_argument(parser, "private_key", "Private Key for Sierra API")
        ServiceTaskBase.add_cli_argument(parser, "data_feed", "Choose a data feed", choices=["apa"])

    def authenticate(self):
        resp = requests.post(url=f"{self.base_uri}{self.token_path}",
                             headers={"Authorization": f"Basic {self.encoded_credentials}",
                                      "Content-Type": "application/x-www-form-urlencoded"})
        print(resp.status_code)
        data = json.loads(resp.text)

        self.auth_token = data["access_token"]
        print(self.auth_token)
        print(time.ctime())
        threading.Timer(self.api_timeout_seconds, self.authenticate).start()


def to_base64(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')
