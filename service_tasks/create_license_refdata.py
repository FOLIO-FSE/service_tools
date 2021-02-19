import json, uuid
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class CreateLicensePolicies(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)

    def do_work(self):
        # licence picklists 
        lp = []
        lp.append({
            "id": "2c91808f725c72b30172718dc71c0048",
            "desc": "InternalContact.Role",
            "internal": "false",
            "values": [
                {
                    "id": "2c91808f725c72b30172718dc72a004b",
                    "value": "license_owner",
                    "label": "License owner"
                    },
                {
                    "id": "2c91808f725c72b30172718dc72f004c",
                    "value": "negotiator",
                    "label": "Negotiator"
                    },
                {
                    "id": "2c91808f725c72b30172718dc7200049",
                    "value": "authorized_signatory",
                    "label": "Authorized signatory"
                    },
                {
                    "id": "2c91808f725c72b30172718dc724004a",
                    "value": "erm_librarian",
                    "label": "ERM Librarian"
                    },
                {
                    "id": "2c91808f725c72b30172718dc734004d",
                    "value": "subject_specialist",
                    "label": "Subject specialist"
                    }
                ]
            })
        lp.append({
            "id": "2c91808f725c72b30172718dc74e0053",
            "desc": "DocumentAttachment.AtType",
            "internal": "false",
            "values": [
                {
                    "id": "2c91808f725c72b30172718dc7510054",
                    "value": "consortium_authorization_statement",
                    "label": "Consortium authorization statement"
                    },
                {
                    "id": "2c91808f725c72b30172718dc7560055",
                    "value": "product_data_sheet",
                    "label": "Product data sheet"
                    },
                {
                    "id": "2c91808f725c72b30172718dc75a0056",
                    "value": "vendor_terms_and_conditions",
                    "label": "Vendor terms and conditions"
                    }
                ]
            })
        lp.append({
                "id": "2c91808f725c72b30172718dc7ef005c",
                "desc": "Yes/No/Other",
                "internal": "false",
                "values": [
                    {
                        "id": "2c91808f725c72b30172718dc7f6005d",
                        "value": "yes",
                        "label": "Yes"
                        },
                    {
                        "id": "2c91808b7445501601764d8de3730031",
                        "value": "not_specified_in_agreement",
                        "label": "Not Specified in Agreement"
                        },
                    {
                        "id": "2c9180857445294501764d8e0ba6005a",
                        "value": "unspecified",
                        "label": "Unspecified"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc802005f",
                        "value": "other_(see_notes)",
                        "label": "Other (see notes)"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7fd005e",
                        "value": "no",
                        "label": "No"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808f725c72b30172718dc6e7003f",
                "desc": "License.EndDateSemantics",
                "internal": "true",
                "values": [
                    {
                        "id": "2c91808f725c72b30172718dc6f70041",
                        "value": "open_ended",
                        "label": "Open ended"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc6ee0040",
                        "value": "explicit",
                        "label": "Explicit"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808f725c72b30172718dc7000042",
                "desc": "License.Status",
                "internal": "true",
                "values": [
                    {
                        "id": "2c91808f725c72b30172718dc7080044",
                        "value": "not_yet_active",
                        "label": "Not yet active"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7040043",
                        "value": "in_negotiation",
                        "label": "In negotiation"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc70d0045",
                        "value": "active",
                        "label": "Active"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7180047",
                        "value": "expired",
                        "label": "Expired"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7120046",
                        "value": "rejected",
                        "label": "Rejected"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808f725c72b30172718dc737004e",
                "desc": "LicenseOrg.Role",
                "internal": "true",
                "values": [
                    {
                        "id": "2c91808f725c72b30172718dc73c004f",
                        "value": "licensor",
                        "label": "Licensor"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc74a0052",
                        "value": "consortium_administrator",
                        "label": "Consortium Administrator"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7450051",
                        "value": "consortium",
                        "label": "Consortium"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7410050",
                        "value": "licensee",
                        "label": "Licensee"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808f725c72b30172718dc8080060",
                "desc": "Permitted/Prohibited",
                "internal": "false",
                "values": [
                    {
                        "id": "2c91808b7445501601764e0501490038",
                        "value": "prohibited_implied",
                        "label": "Prohibited Implied"
                        },
                    {
                        "id": "2c9180857445294501764e04ba0b0060",
                        "value": "permitted_explicit",
                        "label": "Permitted Explicit"
                        },
                    {
                        "id": "2c91808b7445501601764e04a3c80035",
                        "value": "not_specified_in_agreement",
                        "label": "Not Specified in Agreement"
                        },
                    {
                        "id": "2c91808b7445501601764d8e5fa00032",
                        "value": "limited_-_see_notes",
                        "label": "Limited - See Notes"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc8390067",
                        "value": "not_applicable",
                        "label": "Not applicable"
                        },
                    {
                        "id": "2c91808b7445501601764e04ea730037",
                        "value": "prohibited_explicit",
                        "label": "Prohibited Explicit"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc8340066",
                        "value": "unmentioned",
                        "label": "Unmentioned"
                        },
                    {
                        "id": "2c91808b7445501601764e04d1560036",
                        "value": "permitted_implied",
                        "label": "Permitted Implied"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808f725c72b30172718dc75f0057",
                "desc": "License.Type",
                "internal": "false",
                "values": [
                    {
                        "id": "2c9180857445294501764d909457005f",
                        "value": "site_terms_and_conditions",
                        "label": "Site Terms and Conditions"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc76f005b",
                        "value": "alliance",
                        "label": "Alliance"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7670059",
                        "value": "consortial",
                        "label": "Consortial"
                        },
                    {
                        "id": "2c91808b7445501601764d90390f0033",
                        "value": "passive_assent_license_agreement",
                        "label": "Passive Assent License Agreement"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc76b005a",
                        "value": "national",
                        "label": "National"
                        },
                    {
                        "id": "2c91808b7445501601764d90b7ba0034",
                        "value": "unspecified",
                        "label": "Unspecified"
                        },
                    {
                        "id": "2c9180857445294501764e05e4f70061",
                        "value": "signed_license",
                        "label": "Signed License Agreement"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7620058",
                        "value": "local",
                        "label": "Local"
                        },
                    {
                        "id": "2c9180857445294501764d8fde17005b",
                        "value": "click-through_license_agreement",
                        "label": "Click-Through License Agreement"
                        },
                    {
                        "id": "2c9180857445294501764d905818005d",
                        "value": "publisher_has_no_agreement",
                        "label": "Publisher Has No Agreement"
                        },
                    {
                            "id": "2c9180857445294501764d900520005c",
                            "value": "general_policies",
                            "label": "General Policies"
                            }
                    ]
                    })

        lt = []
        lt.append({
        "id": "2c91808b7445501601764d85094f0027",
        "name": "AllRightsReserved",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "All Rights Reserved",
        "description": "All Rights Reserved",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d80dc110048",
        "name": "AlumniAccess",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Alumni Access",
        "description": "Specifies whether alumni have access to the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8d1fcc0030",
        "name": "CopyrightLaw",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Applicable Copyright Law",
        "description": "Specifies the copyright law applicable to the licensed resource",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c91808b7445501601764d8cc248002f",
        "name": "ArchivingAllowed",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Archiving Allowed",
        "description": "Specifies whether the license agreement allows archiving of the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d84aacd004d",
        "name": "ArticleReach",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "ArticleReach",
        "description": "Specifies whether the licensed resource can be included in ArticleReach",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8d88550059",
        "name": "AuthorizedUsers",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Authorized User Definition",
        "description": "Defines what constitutes an authorized user for the licensed resource.",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c91808b7445501601764d7fff640021",
        "name": "ConcurrentUsers",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Concurrent Users",
        "description": "Specifies the number of allowed concurrent users",
        "weight": "0",
        "type": "Integer"
        })
        lt.append({
        "id": "2c9180857445294501764d81e8180049",
        "name": "AgreementConfidentiality",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Confidentiality of Agreement Required",
        "description": "Specifies whether the agreement is bound by confidentiality between licensor and licensee",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d82e8c2004b",
        "name": "UserConfidentiality",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Confidentiality of User Information Protected",
        "description": "Specifies whether a license agreement ensures confidentiality of user information",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8bf829002e",
        "name": "CopyDigital",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Copy - Digital",
        "description": "Specifies whether the agreement allows for digital copies of the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d81922e0023",
        "name": "CopyPrint",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Copy - Print",
        "description": "Specifies whether the agreement allows for physical copies of the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8b3534002c",
        "name": "CoursePackElectronic",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Course Pack - Electronic",
        "description": "Specifies whether the agreement allows for inclusion of the licensed resource in electronic course packs",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8ba1d3002d",
        "name": "CoursePackPrint",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Course Pack - Print",
        "description": "Specifies whether the agreement allows for inclusion of the licensed resource in print course packs",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8ad72c0057",
        "name": "DistanceEducation",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Distance Education",
        "description": "Specifies whether the licensed resource can be used in distance education",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d862662002a",
        "name": "FairDealingClause",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Fair Dealing Clause",
        "description": "Specifies whether an agreement contains a fair dealing clause and provides information pertaining to the clause, when applicable",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8a84450056",
        "name": "FairUseClause",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc7ef005c",
        "desc": "Yes/No/Other",
        "internal": "false",
        "values": [
        {
        "id": "2c91808f725c72b30172718dc7fd005e",
        "value": "no",
        "label": "No"
        },
        {
        "id": "2c91808f725c72b30172718dc7f6005d",
        "value": "yes",
        "label": "Yes"
        },
        {
        "id": "2c91808b7445501601764d8de3730031",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c9180857445294501764d8e0ba6005a",
        "value": "unspecified",
        "label": "Unspecified"
        },
        {
        "id": "2c91808f725c72b30172718dc802005f",
        "value": "other_(see_notes)",
        "label": "Other (see notes)"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "Fair Use Clause",
        "description": "Specifies whether the agreement contains a fair use clause",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d84517b0026",
        "name": "GovJurisdiction",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Governing Jurisdiction",
        "description": "Details the governing jurisdiction of the license agreement",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c91808b7445501601764d8402a90025",
        "name": "GovLaw",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Governing Law",
        "description": "Details the governing law of the license agreement",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c9180857445294501764d8a251b0055",
        "name": "ILLElectronic",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "ILL - Electronic",
        "description": "Specifies whether the resource is licensed for electronic ILL",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d896591002b",
        "name": "ILLElectronicSecure",
        "primary": "true",
        "category": {
        "id": "2c91808f725c72b30172718dc8080060",
        "desc": "Permitted/Prohibited",
        "internal": "false",
        "values": [
        {
        "id": "2c91808b7445501601764e0501490038",
        "value": "prohibited_implied",
        "label": "Prohibited Implied"
        },
        {
        "id": "2c91808b7445501601764e04a3c80035",
        "value": "not_specified_in_agreement",
        "label": "Not Specified in Agreement"
        },
        {
        "id": "2c91808b7445501601764d8e5fa00032",
        "value": "limited_-_see_notes",
        "label": "Limited - See Notes"
        },
        {
        "id": "2c91808b7445501601764e04ea730037",
        "value": "prohibited_explicit",
        "label": "Prohibited Explicit"
        },
        {
        "id": "2c91808f725c72b30172718dc8340066",
        "value": "unmentioned",
        "label": "Unmentioned"
        },
        {
        "id": "2c91808f725c72b30172718dc8390067",
        "value": "not_applicable",
        "label": "Not applicable"
        },
        {
        "id": "2c91808b7445501601764e04d1560036",
        "value": "permitted_implied",
        "label": "Permitted Implied"
        },
        {
        "id": "2c9180857445294501764e04ba0b0060",
        "value": "permitted_explicit",
        "label": "Permitted Explicit"
        }
        ]
        },
        "defaultInternal": "true",
        "label": "ILL - Electronic (Secure)",
        "description": "Specifies whether the resource is licensed for secure electronic ILL",
        "weight": "0",
        "type": "Refdata"
        })
        self.add_policy("policies", lp, "licenses/refdata")
        self.add_policy("terms", lt, "licenses/custprops")

    def add_policy(self, description, policy_array, url):
        print(f"\n------------------- Creating license {description} --------------\n")

        for policy in policy_array:
            resp = requests.post(f"{self.folio_client.okapi_url}/{url}", data=json.dumps(policy), headers=self.folio_client.okapi_headers)
            print(f"{resp.content}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
