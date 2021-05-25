import json, uuid
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class CreatePermissionSets(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)

    def do_work(self):
        circ = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "Circulation",
                "id" : str(uuid.uuid4()),
                "description" : "For all users who work in the circulation desk.", 
                "tags" : [ ],
                "subPermissions" : ["ui-inventory.all-permissions.TEMPORARY","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.statistical-codes","ui-inventory.settings.statistical-code-types","ui-inventory.settings.materialtypes","ui-inventory.settings.instance-types","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.loantypes","ui-inventory.settings.item-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.instance-note-types","ui-inventory.settings.identifier-types","ui-inventory.settings.classification-types","ui-inventory.settings.ill-policies","ui-inventory.settings.holdings-types","ui-inventory.settings.holdings-note-types","ui-inventory.settings.instance-formats","ui-inventory.settings.contributor-types","ui-inventory.settings.call-number-types","ui-inventory.settings.alternative-title-types"],
                "mutable" : "true",
                "visible" : "true"
                }
        prc = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "Print Resource Cataloging",
                "id" : str(uuid.uuid4()),
                "description" : "For all users working with cataloging of print resources (monographs and serials).", 
                "tags" : [ ],
                "subPermissions" : ["ui-inventory.all-permissions.TEMPORARY","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.statistical-codes","ui-inventory.settings.statistical-code-types","ui-inventory.settings.materialtypes","ui-inventory.settings.instance-types","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.loantypes","ui-inventory.settings.item-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.instance-note-types","ui-inventory.settings.identifier-types","ui-inventory.settings.classification-types","ui-inventory.settings.ill-policies","ui-inventory.settings.holdings-types","ui-inventory.settings.holdings-note-types","ui-inventory.settings.instance-formats","ui-inventory.settings.contributor-types","ui-inventory.settings.call-number-types","ui-inventory.settings.alternative-title-types"],
                "mutable" : "true",
                "visible" : "true"
                }
        pra = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "Print Resource Acquisition",
                "id" : str(uuid.uuid4()),
                "description" : "For all users working with aquisition of print resources (monographs and serials).", 
                "tags" : [ ],
                "subPermissions" : ["ui-organizations.delete","ui-notes.item.create","ui-notes.item.edit","ui-notes.item.assign-unassign","ui-orders.acq.unit.assignment.manage","module.notes.enabled","ui-orders.acq.unit.assignment.assign","ui-orders.order.delete","ui-finance.acq.unit.assignment.manage","settings.orders.enabled","ui-notes.item.delete","ui-orders.order.create","ui-organizations.edit","ui-organizations.create","module.orders.enabled","ui-orders.order-lines.delete","ui-finance.acq.unit.assignment.assign","module.organizations.enabled","ui-orders.order.edit","ui-inventory.all-permissions.TEMPORARY","ui-orders.order.view","ui-orders.order-lines.edit","ui-notes.item.view","ui-orders.order-lines.create","ui-orders.order-lines.view"],
                "mutable" : "true",
                "visible" : "true"
                }
        erm = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "Electronic Resource Management",
                "id" : str(uuid.uuid4()),
                "description" : "For users who manage electronic resources.", 
                "tags" : [ ],
                "subPermissions" : ["ui-organizations.settings","ui-organizations.delete","ui-organizations.create","ui-organizations.edit","ui-organizations.view","ui-agreements.agreements.edit","ui-agreements.agreements.view","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect","ui-erm-usage.view","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-organizations.creds.view","ui-organizations.creds.manage","settings.agreements.enabled","ui-eholdings.settings.kb","ui-eholdings.settings.root-proxy","settings.licenses.enabled","settings.notes.enabled","settings.organizations.enabled","settings.tags.enabled","module.search.enabled","module.eholdings.enabled","module.organizations.enabled","module.agreements.enabled","module.notes.enabled","ui-users.view"],
                "mutable" : "true",
                "visible" : "true"
                }
        erm_view = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "ERM Admin",
                "id" : str(uuid.uuid4()),
                "description" : "All authorizations for ERM and also permissions for system settings", 
                "tags" : [ ],
                "subPermissions" : ["ui-agreements.resources.view","ui-plugin-find-license.search","ui-licenses.licenses.delete","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-local-kb-admin.jobs.edit","ui-local-kb-admin.jobs.delete","ui-local-kb-admin.kbs.manage","ui-local-kb-admin.jobs.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.acq.unit.assignment.manage","ui-orders.order.delete","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.creds.manage","ui-organizations.create","ui-organizations.delete","settings.agreements.enabled","ui-myprofile.settings.change-password","settings.notes.enabled","module.orders.enabled","module.notes.enabled"],
                "mutable" : "true",
                "visible" : "true"
                }
        erm_admin = {
                "permissionName" : str(uuid.uuid4()),
                "displayName" : "ERM view only",
                "id" : str(uuid.uuid4()),
                "description" : "For users that look at but never edit agreements and licenses. E.g. staff who work with publishing support for researchers.", 
                "tags" : [ ],
                "subPermissions" : ["ui-erm-usage.view","module.agreements.enabled","ui-notes.item.view","ui-licenses.licenses.view","ui-organizations.view","ui-notes.item.create","ui-agreements.agreements.view","ermusage.view"],
                "mutable" : "true",
                "visible" : "true"
                }
        print(f"\n------------------- Results from creating circ set --------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(circ), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")
        print(f"\n------------------- Results from creating cataloging set for print --------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(prc), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")
        print(f"\n------------------- Results from creating acq set for print--------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(pra), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")
        print(f"\n------------------- Results from creating set for erm operator --------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(erm), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")
        print(f"\n------------------- Results from creating set for erm view only --------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(erm_view), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")
        print(f"\n------------------- Results from creating set for erm admin --------------\n")
        resp = requests.post(f"{self.folio_client.okapi_url}/perms/permissions", data=json.dumps(erm_admin), headers=self.folio_client.okapi_headers)
        print(f"{resp.content}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
