import json, uuid
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class CreateErmPermissionSets(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)

    def do_work(self):
        ps = []
        ps.append({
                "permissionName" : "c1b35cb5-a1ff-4d2c-a6a4-b8a8dbe3edae",
                "displayName" : "Electronic Resource Management",
                "id" : "02f05a09-60f1-46d3-8e14-930bb8ce81c0",
                "description" : "For users who manage electronic resources.", 
                "tags" : [ ],
                "subPermissions" : ["ui-organizations.settings","ui-organizations.delete","ui-organizations.create","ui-organizations.edit","ui-organizations.view","ui-agreements.agreements.edit","ui-agreements.agreements.view","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect","ui-erm-usage.view","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-organizations.creds.view","ui-organizations.creds.manage","settings.agreements.enabled","ui-eholdings.settings.kb","ui-eholdings.settings.root-proxy","settings.licenses.enabled","settings.notes.enabled","settings.organizations.enabled","settings.tags.enabled","module.search.enabled","module.eholdings.enabled","module.organizations.enabled","module.agreements.enabled","module.notes.enabled","ui-users.view"],
                "mutable" : "true",
                "visible" : "true"
                })
        ps.append({
                "permissionName" : "ce7f73f4-6714-4973-aeff-c7af887564b2",
                "displayName" : "ERM Admin",
                "id" : "26b717c6-0d13-4e96-aeda-dfb63c432a29",
                "description" : "All authorizations for ERM and also permissions for system settings", 
                "tags" : [ ],
                "subPermissions" : ["ui-agreements.resources.view","ui-plugin-find-license.search","ui-licenses.licenses.delete","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-local-kb-admin.jobs.edit","ui-local-kb-admin.jobs.delete","ui-local-kb-admin.kbs.manage","ui-local-kb-admin.jobs.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.acq.unit.assignment.manage","ui-orders.order.delete","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.creds.manage","ui-organizations.create","ui-organizations.delete","settings.agreements.enabled","ui-myprofile.settings.change-password","settings.notes.enabled","module.orders.enabled","module.notes.enabled"],
                "mutable" : "true",
                "visible" : "true"
                })
        ps.append({
                "permissionName" : "9399d79e-e500-44ee-8466-f55652596131",
                "displayName" : "ERM view only",
                "id" : "a53b7dac-13b1-497e-9581-c2144a437ad7",
                "description" : "For users that look at but never edit agreements and licenses. E.g. staff who work with publishing support for researchers.", 
                "tags" : [ ],
                "subPermissions" : ["ui-erm-usage.view","module.agreements.enabled","ui-notes.item.view","ui-licenses.licenses.view","ui-organizations.view","ui-notes.item.create","ui-agreements.agreements.view","ermusage.view"],
                "mutable" : "true",
                "visible" : "true"
                })

        for policyset in ps:
            resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(policyset), headers=self.folio_client.okapi_headers)
            print(f"{resp.content}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
