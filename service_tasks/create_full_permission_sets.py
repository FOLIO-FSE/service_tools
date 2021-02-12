import json, uuid
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class CreateFullPermissionSets(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)

    def do_work(self):
        ps = []
        ps.append({
        "permissionName": "4a281bb2-4754-462c-923a-4d3c664d2315",
        "displayName": "acq-admin",
        "id": "3f609993-82dc-484a-9cef-9c7c7e2f5f39",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-agreements.agreements.delete","ui-agreements.agreements.edit","ui-agreements.resources.edit","ui-agreements.agreements.view","ui-agreements.resources.view","ui-finance.acq.unit.assignment.assign","ui-finance.allocations.create","ui-finance.transfers.create","ui-finance.acq.unit.assignment.manage","ui-finance.fiscal-year.view","ui-finance.fund-budget.view","ui-finance.group.view","ui-finance.ledger.view","ui-finance.fiscal-year.edit","ui-finance.fund-budget.edit","ui-finance.group.edit","ui-finance.ledger.edit","ui-finance.fiscal-year.create","ui-finance.fund-budget.create","ui-finance.group.create","ui-finance.ledger.create","ui-finance.fiscal-year.delete","ui-finance.fund-budget.delete","ui-finance.group.delete","ui-finance.ledger.delete","ui-plugin-find-agreement.search","ui-inventory.all-permissions.TEMPORARY","ui-inventory.items.mark-items-withdrawn","ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.view-staff-suppressed-records","ui-inventory.instance.view","ui-inventory.holdings.create","ui-inventory.instance.create","ui-inventory.item.create","ui-inventory.holdings.edit","ui-inventory.instance.edit","ui-inventory.item.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-invoice.approve","ui-invoice.acq.unit.assignment.assign","ui-invoice.batchVoucher.download","ui-invoice.acq.unit.assignment.manage","ui-invoice.pay","ui-invoice.all","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.acq.unit.assignment.manage","ui-orders.order.delete","ui-orders.order.reopen","ui-orders.order.unopen","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.acqUnits.assign","ui-organizations.creds.view","ui-organizations.creds.manage","ui-organizations.acqUnits.manage","ui-organizations.view","ui-organizations.edit","ui-organizations.create","ui-organizations.delete","ui-receiving.view","ui-receiving.edit","ui-receiving.create","ui-receiving.delete","ui-requests.all","ui-requests.moveRequest","ui-requests.reorderQueue","ui-requests.view","ui-requests.create","ui-requests.edit","ui-agreements.generalSettings.manage","ui-agreements.supplementaryProperties.manage","ui-agreements.picklists.manage","ui-finance.settings.all","ui-inventory.settings.hrid-handling","ui-inventory.settings.ill-policies","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.alternative-title-types","ui-inventory.settings.call-number-types","ui-inventory.settings.classification-types","ui-inventory.settings.contributor-types","ui-inventory.settings.instance-formats","ui-inventory.settings.holdings-note-types","ui-inventory.settings.holdings-types","ui-inventory.settings.instance-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.item-note-types","ui-inventory.settings.loantypes","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.instance-types","ui-inventory.settings.materialtypes","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.identifier-types","ui-inventory.settings.statistical-code-types","ui-inventory.settings.statistical-codes","ui-inventory.settings.list.view","settings.invoice.enabled","settings.orders.enabled","ui-organizations.settings","ui-receiving.settings","ui-users.settings.addresstypes","ui-users.settings.feefines.all","ui-users.settings.comments","ui-users.settings.feefines","ui-users.settings.owners","ui-users.settings.conditions","ui-users.settings.limits","ui-users.settings.usergroups","ui-users.settings.payments","ui-users.settings.permsets","ui-users.settings.profilePictures","ui-users.settings.refunds","ui-users.settings.transfertypes","ui-users.settings.waives","ui-users.settings.customfields.edit","ui-users.settings.customfields.all","ui-users.settings.customfields.view","ui-developer.settings.passwd","ui-eholdings.settings.kb","ui-eholdings.settings.kb.delete","ui-eholdings.settings.root-proxy","settings.eholdings.enabled","ui-eholdings.settings.access-types.create-edit","ui-eholdings.settings.access-types.all","ui-eholdings.settings.access-types.view","module.invoice.enabled","ui-users.editperms","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view","ui-users.loans.all","ui-users.requests.all","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "aef207f7-ac3a-4d7b-968c-3c0c59874c4e",
        "displayName": "acq-manager",
        "id": "80b566cc-058e-49be-a507-312840da4aee",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-agreements.agreements.delete","ui-agreements.agreements.edit","ui-agreements.resources.edit","ui-agreements.agreements.view","ui-agreements.resources.view","ui-finance.acq.unit.assignment.assign","ui-finance.allocations.create","ui-finance.transfers.create","ui-finance.acq.unit.assignment.manage","ui-finance.fiscal-year.view","ui-finance.fund-budget.view","ui-finance.group.view","ui-finance.ledger.view","ui-finance.fiscal-year.edit","ui-finance.fund-budget.edit","ui-finance.group.edit","ui-finance.ledger.edit","ui-finance.fiscal-year.create","ui-finance.fund-budget.create","ui-finance.group.create","ui-finance.ledger.create","ui-finance.fiscal-year.delete","ui-finance.fund-budget.delete","ui-finance.group.delete","ui-finance.ledger.delete","ui-plugin-find-agreement.search","ui-inventory.items.mark-items-withdrawn","ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.view-staff-suppressed-records","ui-inventory.instance.view","ui-inventory.holdings.create","ui-inventory.instance.create","ui-inventory.item.create","ui-inventory.holdings.edit","ui-inventory.instance.edit","ui-inventory.item.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-invoice.approve","ui-invoice.acq.unit.assignment.assign","ui-invoice.batchVoucher.download","ui-invoice.acq.unit.assignment.manage","ui-invoice.pay","ui-invoice.all","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.acq.unit.assignment.manage","ui-orders.order.delete","ui-orders.order.reopen","ui-orders.order.unopen","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.acqUnits.assign","ui-organizations.creds.view","ui-organizations.creds.manage","ui-organizations.acqUnits.manage","ui-organizations.view","ui-organizations.edit","ui-organizations.create","ui-organizations.delete","ui-receiving.view","ui-receiving.edit","ui-receiving.create","ui-receiving.delete","ui-requests.moveRequest","ui-requests.reorderQueue","ui-requests.view","ui-requests.create","ui-requests.edit","module.eholdings.enabled","module.invoice.enabled","ui-users.editperms","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view","ui-users.loans.all","ui-users.requests.all","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "dc34c1c7-ea7b-466a-bad4-1dc3f535c0f3",
        "displayName": "acq-observer",
        "id": "42d75160-7444-492a-8eb5-833aa9fdb876",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-agreements.agreements.view","ui-agreements.resources.view","ui-finance.fiscal-year.view","ui-finance.fund-budget.view","ui-finance.group.view","ui-finance.ledger.view","ui-plugin-find-agreement.search","ui-inventory.instance.view-staff-suppressed-records","ui-inventory.instance.view","ui-invoice.all","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.order.delete","ui-orders.order.reopen","ui-orders.order.unopen","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.creds.view","ui-organizations.view","ui-receiving.view","ui-requests.view","module.invoice.enabled","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.loans.view","ui-users.requests.all","ui-eholdings.package-title.select-unselect" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "1a6de405-ea48-4f03-89cf-45ca9b0c1662",
        "displayName": "acq-staff",
        "id": "8161cc86-916f-40da-89c3-394fed8d092f",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-agreements.agreements.edit","ui-agreements.resources.edit","ui-agreements.agreements.view","ui-agreements.resources.view","ui-finance.acq.unit.assignment.assign","ui-finance.fiscal-year.view","ui-finance.fund-budget.view","ui-finance.group.view","ui-finance.ledger.view","ui-finance.fiscal-year.edit","ui-finance.fund-budget.edit","ui-finance.group.edit","ui-finance.ledger.edit","ui-finance.fiscal-year.create","ui-finance.fund-budget.create","ui-finance.group.create","ui-finance.ledger.create","ui-plugin-find-agreement.search","ui-inventory.items.mark-items-withdrawn","ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.view-staff-suppressed-records","ui-inventory.instance.view","ui-inventory.holdings.create","ui-inventory.instance.create","ui-inventory.item.create","ui-inventory.holdings.edit","ui-inventory.instance.edit","ui-inventory.item.edit","ui-inventory.item.markasmissing","ui-invoice.acq.unit.assignment.assign","ui-invoice.batchVoucher.download","ui-invoice.all","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.order.delete","ui-orders.order.reopen","ui-orders.order.unopen","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.acqUnits.assign","ui-organizations.creds.view","ui-organizations.creds.manage","ui-organizations.view","ui-organizations.edit","ui-organizations.create","ui-receiving.view","ui-receiving.edit","ui-receiving.create","ui-requests.moveRequest","ui-requests.reorderQueue","ui-requests.view","ui-requests.create","ui-requests.edit","module.invoice.enabled","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view","ui-users.loans.all","ui-users.requests.all","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "da689b33-5d8f-4134-b838-093bc124e47b",
        "displayName": "cataloger",
        "id": "804720a4-405c-4176-850d-d556c861f384",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-inventory.settings.ill-policies","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.alternative-title-types","ui-inventory.settings.call-number-types","ui-inventory.settings.classification-types","ui-inventory.settings.contributor-types","ui-inventory.settings.instance-formats","ui-inventory.settings.holdings-note-types","ui-inventory.settings.holdings-types","ui-inventory.settings.instance-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.item-note-types","ui-inventory.settings.loantypes","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.instance-types","ui-inventory.settings.materialtypes","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.identifier-types","ui-inventory.settings.statistical-code-types","ui-inventory.settings.statistical-codes","ui-inventory.settings.list.view","settings.data-export.enabled","settings.data-import.enabled","ui-quick-marc.quick-marc-editor.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "f744f17d-8c38-459a-b953-a94d6e0686fc",
        "displayName": "checkin-all",
        "id": "67919963-8f5d-4222-9ccd-7bf35173985d",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "08eadbb0-cdf0-40d9-afb7-0fed8393efb4",
        "displayName": "checkout-all",
        "id": "6d4c762f-166a-41f1-8251-fe48f6d7c8cb",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkout.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "d7773363-43cf-4524-ab44-ba6a3b2c7e58",
        "displayName": "circ-admin",
        "id": "bf0a7efb-725a-4dea-bf4c-6d0aa3ecd875",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all","ui-checkout.all","ui-plugin-create-inventory-records.create","ui-users.feefineactions","ui-inventory.instance.view","ui-inventory.item.markasmissing","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-requests.all","ui-calendar.edit","ui-calendar.view","ui-circulation.settings.cancellation-reasons","ui-circulation.settings.circulation-rules","ui-circulation.settings.fixed-due-date-schedules","ui-circulation.settings.loan-policies","ui-circulation.settings.lost-item-fees-policies","ui-circulation.settings.notice-policies","ui-circulation.settings.other-settings","ui-circulation.settings.overdue-fines-policies","ui-circulation.settings.notice-templates","ui-circulation.settings.request-policies","ui-circulation.settings.staff-slips","ui-circulation.settings.loan-history","course-reserves.maintain-settings","ui-users.settings.feefines.all","settings.courses.enabled","module.notes.enabled","ui-users.editperms","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view","ui-users.requests.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "df1e89d0-530b-488a-916d-3298964092a2",
        "displayName": "circ-manager",
        "id": "fc25422c-212d-4850-8a53-a8a3c4bffe7f",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all","ui-checkout.all","ui-plugin-create-inventory-records.create","ui-users.feefineactions","ui-inventory.instance.view","ui-inventory.item.markasmissing","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-requests.all","module.notes.enabled","ui-users.editperms","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view","ui-users.requests.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "ce870d50-1aca-4ecd-9f90-0f32f1fe15b5",
        "displayName": "circ-observer",
        "id": "7b02d4cf-69ba-42de-bb10-31b980c9d617",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all","ui-checkout.circulation","ui-inventory.instance.view","ui-notes.item.view","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.loans.view","ui-users.requests.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "23799739-ed31-406a-ba98-d2b557143245",
        "displayName": "circ-staff",
        "id": "413d9747-2fe9-4cb6-ac2e-ff6a3c501850",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all","ui-checkout.all","ui-plugin-create-inventory-records.create","ui-inventory.instance.view","ui-inventory.item.markasmissing","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-requests.all","module.notes.enabled","ui-users.editperms","ui-users.edituserservicepoints","ui-users.create","ui-users.feesfines.actions.all","ui-users.patron_blocks","ui-users.editproxies","ui-users.edit","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.reset.password","ui-users.loans.edit","ui-users.loans.claim-item-returned","ui-users.loans.declare-item-lost","ui-users.loans.declare-claimed-returned-item-as-missing","ui-users.loans.renew","ui-users.loans.renew-override","ui-users.loans.view" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "68a5c528-4c3f-4e97-ad2e-c5c7d1ed9ce6",
        "displayName": "circ-student",
        "id": "7ada0f63-a1a1-4e86-9481-91d90b519bd3",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-checkin.all","ui-checkout.circulation","ui-plugin-create-inventory-records.create","ui-inventory.instance.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.view","ui-requests.create","module.notes.enabled","ui-users.viewperms","ui-users.viewproxies","ui-users.viewuserservicepoints","ui-users.view","ui-users.loans.renew","ui-users.loans.view","ui-users.requests.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "fba7276e-55fa-4fd6-811c-c99b92857e1a",
        "displayName": "copy-cataloger",
        "id": "21ea69dd-f1a4-46ce-ad66-e410a47c64c9",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-inventory.items.mark-items-withdrawn","ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-inventory.settings.list.view","settings.data-export.enabled","settings.data-import.enabled","module.data-export.enabled","ui-quick-marc.quick-marc-editor.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "192f7c8c-3f7b-407b-8e58-7afe0cfc222d",
        "displayName": "data-export-admin",
        "id": "80b90983-d99e-46a8-90f8-746e46664c13",
        "description": "",
        "tags": [],
        "subPermissions": [ "settings.data-export.enabled" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "77d56178-c9ba-4b40-bbc2-1c7b8866a10b",
        "displayName": "data-export",
        "id": "fb199c75-b1bb-40c4-91a1-b84421d95eeb",
        "description": "",
        "tags": [],
        "subPermissions": [ "module.data-export.enabled" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "6284f563-6774-49bf-8699-ba4c0fe01e7a",
        "displayName": "data-import",
        "id": "b1c7024e-7238-4c0f-aa73-80e76c4ead88",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-inventory.settings.list.view","settings.data-import.enabled","module.data-import.enabled" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "bf17caf9-178b-4b6b-8e67-888a69efff92",
        "displayName": "metadata-admin",
        "id": "11db8bd3-424c-4b35-9511-89043b1bb992",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-inventory.settings.hrid-handling","ui-inventory.settings.ill-policies","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.alternative-title-types","ui-inventory.settings.call-number-types","ui-inventory.settings.classification-types","ui-inventory.settings.contributor-types","ui-inventory.settings.instance-formats","ui-inventory.settings.holdings-note-types","ui-inventory.settings.holdings-types","ui-inventory.settings.instance-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.item-note-types","ui-inventory.settings.loantypes","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.instance-types","ui-inventory.settings.materialtypes","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.identifier-types","ui-inventory.settings.statistical-code-types","ui-inventory.settings.statistical-codes","ui-inventory.settings.list.view","settings.data-export.enabled","settings.data-import.enabled","module.data-export.enabled","ui-quick-marc.quick-marc-editor.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "f411209c-ccbb-4add-8c34-243ddf981033",
        "displayName": "quick-marc-all",
        "id": "d3be3df3-af3d-41a2-bbff-e95e7e25610e",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-quick-marc.quick-marc-editor.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "1ef2de3f-c4ac-4680-be05-2eac6e529efa",
        "displayName": "technical-service-staff",
        "id": "4c50e460-1d4d-4d9c-92b4-50a65c4a4f63",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-inventory.items.mark-items-withdrawn","ui-inventory.holdings.move","ui-inventory.item.move","ui-inventory.instance.edit","ui-inventory.holdings.delete","ui-inventory.item.delete","ui-inventory.item.markasmissing","ui-inventory.settings.hrid-handling","ui-inventory.settings.ill-policies","ui-inventory.settings.electronic-access-relationships","ui-inventory.settings.alternative-title-types","ui-inventory.settings.call-number-types","ui-inventory.settings.classification-types","ui-inventory.settings.contributor-types","ui-inventory.settings.instance-formats","ui-inventory.settings.holdings-note-types","ui-inventory.settings.holdings-types","ui-inventory.settings.instance-note-types","ui-inventory.settings.instance-statuses","ui-inventory.settings.item-note-types","ui-inventory.settings.loantypes","ui-inventory.settings.modes-of-issuance","ui-inventory.settings.instance-types","ui-inventory.settings.materialtypes","ui-inventory.settings.nature-of-content-terms","ui-inventory.settings.identifier-types","ui-inventory.settings.statistical-code-types","ui-inventory.settings.statistical-codes","ui-inventory.settings.list.view","settings.data-export.enabled","settings.data-import.enabled","module.data-export.enabled","module.data-import.enabled","ui-quick-marc.quick-marc-editor.all" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
        "permissionName": "f1eb719b-f496-4532-8029-f4d667e95784",
        "displayName": "user-basic-view",
        "id": "3aac14f2-f755-488b-8052-ae4fbcd73cbd",
        "description": "",
        "tags": [],
        "subPermissions": [ "ui-users.view" ],
        "mutable" : "true",
        "visible" : "true"
        })
        ps.append({
                "permissionName" : "c1b35cb5-a1ff-4d2c-a6a4-b8a8dbe3edae",
                "displayName" : "erm-user",
                "id" : "02f05a09-60f1-46d3-8e14-930bb8ce81c0",
                "description" : "For users who manage electronic resources.", 
                "tags" : [ ],
                "subPermissions" : ["ui-organizations.settings","ui-organizations.delete","ui-organizations.create","ui-organizations.edit","ui-organizations.view","ui-agreements.agreements.edit","ui-agreements.agreements.view","ui-eholdings.titles-packages.create-delete","ui-eholdings.records.edit","ui-eholdings.package-title.select-unselect","ui-erm-usage.view","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-organizations.creds.view","ui-organizations.creds.manage","settings.agreements.enabled","ui-eholdings.settings.kb","ui-eholdings.settings.root-proxy","settings.licenses.enabled","settings.notes.enabled","settings.organizations.enabled","settings.tags.enabled","module.search.enabled","module.eholdings.enabled","module.organizations.enabled","module.agreements.enabled","module.notes.enabled","ui-users.view"],
                "mutable" : "true",
                "visible" : "true"
                })
        ps.append({
                "permissionName" : "ce7f73f4-6714-4973-aeff-c7af887564b2",
                "displayName" : "erm-admin",
                "id" : "26b717c6-0d13-4e96-aeda-dfb63c432a29",
                "description" : "All authorizations for ERM and also permissions for system settings", 
                "tags" : [ ],
                "subPermissions" : ["ui-agreements.resources.view","ui-plugin-find-license.search","ui-licenses.licenses.delete","ui-licenses.licenses.edit","ui-licenses.licenses.view","ui-local-kb-admin.jobs.edit","ui-local-kb-admin.jobs.delete","ui-local-kb-admin.kbs.manage","ui-local-kb-admin.jobs.view","ui-notes.item.assign-unassign","ui-notes.item.create","ui-notes.item.delete","ui-notes.item.edit","ui-notes.item.view","ui-orders.acq.unit.assignment.assign","ui-orders.order-lines.create","ui-orders.order.create","ui-orders.order-lines.delete","ui-orders.order-lines.edit","ui-orders.order.edit","ui-orders.acq.unit.assignment.manage","ui-orders.order.delete","ui-orders.order-lines.view","ui-orders.order.view","ui-organizations.creds.manage","ui-organizations.create","ui-organizations.delete","settings.agreements.enabled","ui-myprofile.settings.change-password","settings.notes.enabled","module.orders.enabled","module.notes.enabled"],
                "mutable" : "true",
                "visible" : "true"
                })
        ps.append({
                "permissionName" : "9399d79e-e500-44ee-8466-f55652596131",
                "displayName" : "erm-view-only",
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
