from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase
from service_tasks import *
import argparse

def parse_args(task_classes):
    """Parse CLI Arguments"""
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(help="commands", dest="command")
    for task_class in task_classes:
        sub_parser = subs.add_parser(task_class.__name__)
        task_class.add_arguments(sub_parser)
    args = parser.parse_args()
    print(args)
    return args


def main():
    task_classes = inheritors(ServiceTaskBase)
    args = parse_args(task_classes)
    task_class = next(tc for tc in task_classes if tc.__name__ == args.command)
    if "okapi_credentials_string" in args and args.okapi_credentials_string:
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
