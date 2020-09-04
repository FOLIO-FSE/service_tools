import json

from folioclient import FolioClient
from gooey import Gooey, GooeyParser

from service_tasks.service_task_base import ServiceTaskBase
from service_tasks import *

def parse_args(task_classes):
    """Parse CLI Arguments"""
    parser = GooeyParser(description="My Cool Gooey App!")
    subs = parser.add_subparsers(help="commands", dest="command")
    for task_class in task_classes:
        sub_parser = subs.add_parser(task_class.__name__)
        add_common_arguments(sub_parser)
        task_class.add_arguments(sub_parser)
    args = parser.parse_args()
    return args


def add_common_arguments(parser):
    parser.add_argument(
        "okapi_credentials_string", help=("URL, TENANT_ID,  USERNAME, PASSWORD")
    )


@Gooey(
    advanced=True,
    progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
    progress_expr="current / total * 100",
    required_cols = 1,
    optional_cols=0,
    default_size=[1100,800],
    program_name="FOLIO Service task helper"
)
def main():
    task_classes = inheritors(ServiceTaskBase)
    args = parse_args(task_classes)
    task_class = next(tc for tc in task_classes if tc.__name__ == args.command)
    if args.okapi_credentials_string:
        okapi_credentials = args.okapi_credentials_string.split(" ")
        folio_client = FolioClient(
            okapi_credentials[0],
            okapi_credentials[1],
            okapi_credentials[2],
            okapi_credentials[3],
        )
        task_obj = task_class(folio_client, args)
    else:
        task_obj = task_class(args)
    print(args.command)
    task_obj.do_work()


def inheritors(base_class):
    subclasses = set()
    work = [base_class]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


if __name__ == "__main__":
    main()
