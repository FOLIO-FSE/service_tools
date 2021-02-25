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
        #
        # Note that FOLIO ignores IDs in license policies. If you
        # add others that are linked to terms, you MUST add a routine
        # that discovers which ID FOLIO created
        lp = []
        lp.append({
                "id": "2c91808b768637530177d0d8d6c5024d",
                "desc": "Yes/No/Other",
                "internal": "false",
                "values": [
                    {
                        "id": "2c91808f725c72b30172718dc7f6005d",
                        "value": "yes",
                        "label": "Yes"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc7fd005e",
                        "value": "no",
                        "label": "No"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc802005f",
                        "value": "other",
                        "label": "Other"
                        }
                    ]
                })
        lp.append({
                "id": "2c91808b768637530177d0d8d9e80251",
                "desc": "Permitted/Prohibited",
                "internal": "false",
                "values": [
                    {
                        "id": "2c9180857445294501764e04ba0b0060",
                        "value": "permitted",
                        "label": "Permitted"
                        },
                    {
                        "id": "2c91808b7445501601764d8e5fa00032",
                        "value": "limited",
                        "label": "Limited - See Notes"
                        },
                    {
                        "id": "2c91808b7445501601764e04ea730037",
                        "value": "prohibited",
                        "label": "Prohibited"
                        },
                    {
                        "id": "2c91808f725c72b30172718dc8340066",
                        "value": "unmentioned",
                        "label": "Unmentioned"
                        }
                    ]
                })

        #
        # FOLIO ignores the IDs created for the policies, so we need to find what the real ones are before 
        # connecting them to the license terms
        #
        # first add the policies
        self.add_policy("policies", lp, "licenses/refdata")

        # now figure out what they're called
        url = f'{self.folio_client.okapi_url}/licenses/refdata'
        resp = requests.get(url, headers=self.folio_client.okapi_headers)
        refdata = resp.json()

        for entry in refdata:
            id = entry['id']
            desc = entry['desc']

            if desc == 'Yes/No/Other':
                YesNo = id

            if desc == 'Permitted/Prohibited':
                PermPro = id 

        lt = []
        lt.append({
        "id": "2c91808b7445501601764d85094f0027",
        "name": "AllRightsReserved",
        "primary": "true",
        "category": f"{YesNo}", 
        "defaultInternal": "true",
        "label": "All Rights Reserved",
        "description": "All Rights Reserved",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d80dc110048",
        "name": "AlumniAccess",
        "primary": "false",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Alumni Access",
        "description": "Specifies whether alumni have access to the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8cc248002f",
        "name": "ArchivingAllowed",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Archiving Allowed",
        "description": "Specifies whether the license agreement allows archiving of the licensed resource",
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
        "category": f"{YesNo}",
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
        "category": f"{YesNo}",
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
        "category": f"{PermPro}",
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
        "category": f"{PermPro}",
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
        "category": f"{PermPro}",
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
        "category": f"{PermPro}",
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
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Distance Education",
        "description": "Specifies whether the licensed resource can be used in distance education",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8a84450056",
        "name": "FairUseClause",
        "primary": "true",
        "category": f"{YesNo}",
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
        "category": f"{PermPro}",
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
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "ILL - Electronic (Secure)",
        "description": "Specifies whether the resource is licensed for secure electronic ILL",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d89d1640054",
        "name": "ILLPrint",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "ILL - Print",
        "description": "Specifies whether the resource is licensed for print ILL",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d83b3e9004c",
        "name": "IndemLicensee",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Indemnification by Licensee",
        "description": "Indemnification by Licensee",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c91808b7445501601764d834a780024",
        "name": "IndemLicensor",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Indemnification by Licensor",
        "description": "Indemnification by Licensor",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c9180857445294501764d868c77004e",
        "name": "LMS",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Learning Management System",
        "description": "Specifies whether access to the licensed resource can be provided via the licensee's LMS",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8906e10053",
        "name": "LinkElectronic",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Link Electronic",
        "description": "Specifies whether the licensed resource can be linked electronically for use in courses",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8282c8004a",
        "name": "OtherRestrictions",
        "primary": "true",
        "defaultInternal": "true",
        "label": "Other Restrictions",
        "description": "A blanket term to capture restrictions on a licensed resource not covered by established terms",
        "weight": "0",
        "type": "Text"
        })
        lt.append({
        "id": "2c9180857445294501764d8c5a100058",
        "name": "PerpetualAccess",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Perpetual Access",
        "description": "Specifies whether the agreement provides perpetual access to the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d874d52004f",
        "name": "PersonsPerceptualDisabilities",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Persons with Perceptual Disabilities",
        "description": "Specifies usage guidelines for persons with perceptual disabilities",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8072020047",
        "name": "SERU",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Publisher Accepts SERU",
        "description": "Publisher Accepts SERU",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d88a8390052",
        "name": "ReservesElectronic",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Reserves - Electronic",
        "description": "Specifies whether and how the licensed content can be used in electronic reserves",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d8807a80051",
        "name": "ReservesPrint",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Reserves - Print",
        "description": "Specifies whether and how the licensed content can be used in print reserves",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d85c8030029",
        "name": "DepositRights",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Right to Deposit",
        "description": "Specifies who retains the right to deposit the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8138210022",
        "name": "ScholarlySharing",
        "primary": "true",
        "category": f"{PermPro}",
        "defaultInternal": "true",
        "label": "Scholarly Sharing",
        "description": "Specifies whether a licensed resource permits scholarly sharing",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c91808b7445501601764d8563350028",
        "name": "TextDataMining",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Text / Data Mining",
        "description": "Provides specification around text and data mining of the licensed resource",
        "weight": "0",
        "type": "Refdata"
        })
        lt.append({
        "id": "2c9180857445294501764d87ab1e0050",
        "name": "Walkins",
        "primary": "true",
        "category": f"{YesNo}",
        "defaultInternal": "true",
        "label": "Walk-ins",
        "description": "Specifies whether the licensed resource is available for use to walk-in users",
        "weight": "0",
        "type": "Refdata"
        })
        
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
