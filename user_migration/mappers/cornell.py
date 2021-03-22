import csv
import json
import re
import uuid

from folioclient import FolioClient

from user_migration.mappers.mapper_base import MapperBase


def country_map():
    return {"100000": "US",
            "": "US",
            "11445": "US",
            "14850": "US",
            "31311": "US",
            "Afghanistan": "AF",
            "Argentina": "AR",
            "Australia": "AU",
            "Austria": "AT",
            "Azerbaijan": "AZ",
            "Bahamas": "BS",
            "Bahrain": "BH",
            "Bangladesh": "BD",
            "Barbados": "BB",
            "Belarus": "BY",
            "Belgium": "BE",
            "Belize": "BZ",
            "Bermuda": "BM",
            "Bolivia": "BO",
            "Bosnia and Herzegovi": "BA",
            "Botswana": "BW",
            "Brazil": "BR",
            "Brunei Darussalam": "BN",
            "Bulgaria": "BG",
            "Burundi": "BI",
            "CANADA": "CA",
            "Cameroon": "CM",
            "Canada": "CA",
            "Chile": "CL",
            "China": "CN",
            "Colombia": "COL",
            "Congo": "CG",
            "Costa Rica": "CR",
            "Cote D'Ivoire": "CI",
            "Croatia": "HR",
            "Curacao": "CW",
            "Cyprus": "CY",
            "Czech Republic": "CZ",
            "Denmark": "DK",
            "Dominican Republic": "DO",
            "Ecuador": "EC",
            "Egypt": "EG",
            "El Salvador": "SV",
            "Eritrea": "ER",
            "Estonia": "EE",
            "Ethiopia": "ET",
            "Finland": "FI",
            "Fmr Yugoslav Rep of": "RS",
            "France": "FR",
            "Georgia": "GE",
            "Germany": "DE",
            "Ghana": "GH",
            "Greece": "GR",
            "Guam": "GU",
            "Guatemala": "GT",
            "Guyana": "GY",
            "Haiti": "HT",
            "Honduras": "HN",
            "Hong Kong": "HK",
            "Hungary": "HU",
            "IRELAND": "IE",
            "ISIR Profile Country": "",
            "Iceland": "IS",
            "India": "IN",
            "Indonesia": "ID",
            "Iran (Islamic Republ": "IR",
            "Ireland": "IE",
            "Israel": "IL",
            "Italy": "IT",
            "Jamaica": "JM",
            "Japan": "JP",
            "Jordan": "JO",
            "Kazakhstan": "KZ",
            "Kenya": "KE",
            "Korea, Republic of": "KR",
            "Kuwait": "KW",
            "Latvia": "LV",
            "Lebanon": "LB",
            "Liberia": "LR",
            "Liechtenstein": "LI",
            "Lithuania": "LT",
            "Luxembourg": "LU",
            "Macao": "MO",
            "Madagascar": "MG",
            "Malaysia": "MY",
            "Maldives": "MV",
            "Mauritius": "MU",
            "Mexico": "MX",
            "Moldova, Republic of": "MD",
            "Mongolia": "MN",
            "Montenegro": "ME",
            "Morocco": "MA",
            "Mozambique": "MZ",
            "Myanmar": "MM",
            "NY": "US",
            "Nepal": "NP",
            "Netherlands": "NL",
            "New Zealand": "NZ",
            "Nicaragua": "NI",
            "Niger": "NE",
            "Nigeria": "NG",
            "None": "",
            "Norway": "NO",
            "Oman": "OM",
            "Pakistan": "PK",
            "Panama": "PA",
            "Paraguay": "PY",
            "Peru": "PE",
            "Philippines": "PH",
            "Poland": "PL",
            "Portugal": "PT",
            "Puerto Rico": "PR",
            "Qatar": "QA",
            "Republic of Serbia": "RS",
            "Reunion": "RE",
            "Romania": "RO",
            "Russian Federation": "RU",
            "Rwanda": "RW",
            "SG": "",
            "Saudi Arabia": "SA",
            "Scotland": "UK",
            "Senegal": "SN",
            "Singapore": "SG",
            "Slovakia": "SK",
            "Slovenia": "SL",
            "Solomon Islands": "SB",
            "South Africa": "ZA",
            "Spain": "ES",
            "Sri Lanka": "LK",
            "Sweden": "SE",
            "Switzerland": "CH",
            "Syrian Arab Republic": "SY",
            "Taiwan": "TW",
            "Taiwan, Republic of": "TW",
            "Tanzania, United Rep": "TZ",
            "Thailand": "TH",
            "Tomp": "US",
            "Tompkins": "US",
            "Trinidad and Tobago": "TT",
            "Tunisia": "TN",
            "Turkey": "TR",
            "US": "US",
            "US Minor Outlying Is": "UM",
            "USA": "US",
            "Uganda": "UG",
            "Ukraine": "UA",
            "United Arab Emirates": "AE",
            "United Kingdom": "UK",
            "United States": "US",
            "Uruguay": "UY",
            "Uzbekistan": "UZ",
            "Venezuela": "VE",
            "Viet Nam": "VN",
            "Zambia": "ZM",
            "Zimbabwe": "ZW",
            "us": "US"}


class Cornell(MapperBase):
    def __init__(self, folio_client: FolioClient, args):
        super().__init__(folio_client)
        self.args = args
        self.user_schema = MapperBase.get_user_schema()

    def do_map(self, legacy_user_dict):
        folio_user = self.instantiate_user()
        legacy_user = legacy_user_dict["data"]

        self.add_to_migration_report("Users per patron type", str(legacy_user["patronGroup"]))
        mapped_legacy_props = []

        for prop in self.user_schema["properties"]:

            if prop in legacy_user:  # is there a match in the csv?
                if legacy_user[prop].strip():  # Match! Lets report this
                    folio_user[prop] = legacy_user[prop]
                    mapped_legacy_props.append(prop)
                    self.report_legacy_mapping(prop, True, False)
                    self.report_folio_mapping(prop, True, False)
                else:  # Match but empty field. Lets report this
                    mapped_legacy_props.append(prop)
                    self.report_legacy_mapping(prop, True, True)
                    self.report_folio_mapping(prop, True, True)
            elif prop == "customFields":
                custom_fields = [c for c in legacy_user if c.startswith("customField")]
                if any(custom_fields):
                    for custom_field in custom_fields:
                        folio_user["customFields"][custom_field.split('.')[1]] = legacy_user[custom_field]
                        self.add_to_migration_report("General",
                                                     f"Custom field {custom_field.split('.')[1]} added")
                        self.report_legacy_mapping(prop, True, False)
                        self.report_folio_mapping(prop, True, False)

            else:
                self.report_folio_mapping(prop, False, False)
                # self.report_legacy_mapping(prop, False, False)
        for prop in self.user_schema['properties']['personal']['properties']:
            if prop in legacy_user:  # is there a match in the csv?
                if legacy_user[prop].strip():  # Match! Lets report this
                    folio_user['personal'][prop] = legacy_user[prop]
                    mapped_legacy_props.append(prop)
                    self.report_legacy_mapping(f"{prop}", True, False)
                    self.report_folio_mapping(f"personal.{prop}", True, False)
                else:  # Match but empty field. Lets report this
                    mapped_legacy_props.append(prop)
                    self.report_legacy_mapping(f"{prop}", True, True)
                    self.report_folio_mapping(f"personal.{prop}", True, True)
            else:
                self.report_folio_mapping(f"personal.{prop}", False, False)
        for prop in legacy_user:
            if prop not in mapped_legacy_props:
                if legacy_user[prop].strip():
                    self.report_legacy_mapping(f"{prop}", False, False)
                else:
                    self.report_legacy_mapping(f"{prop}", False, True)
        folio_user['patronGroup'] = self.get_user_group(legacy_user['patronGroup'])
        self.add_to_migration_report("Users by FOLIO Patron Group", folio_user['patronGroup'])
        self.handle_addresses(folio_user, legacy_user_dict)
        self.validate(folio_user)
        if 'dateOfBirth' in folio_user['personal']:
            del folio_user['personal']['dateOfBirth']
        if self.args.temp_email:
            self.add_to_migration_report("General", f"Replaced email with {self.args.temp_email}")
            folio_user["personal"]["email"] = self.args.temp_email
        return folio_user

    def handle_addresses(self, folio_user, legacy_user_dict):
        a = 0
        folio_user['personal']['addresses'] = list()
        primary_set = False
        mapped_types = []
        addresses = legacy_user_dict["addresses"]
        address_types = list([a['addressTypeId'] for a in addresses])
        address_types.sort()
        self.add_to_migration_report("Address type breakdown", "-".join(address_types))
        self.add_to_migration_report("Address type breakdown", f"Patrons with {len(addresses)} address")
        email = ""
        for legacy_address in addresses:
            self.add_to_migration_report("Address Types from Voyager", f"All addresses, total")
            is_duplicate = legacy_address['addressTypeId'].lower() in mapped_types
            if is_duplicate:
                self.add_to_migration_report("Address Types from Voyager",
                                             f"Duplicate of {legacy_address['addressTypeId']}")
            else:
                self.add_to_migration_report("Address Types from Voyager", f"{legacy_address['addressTypeId']}")
                mapped_types.append(legacy_address['addressTypeId'].lower())
                if legacy_address['addressTypeId'].lower() == "email" or folio_user['personal'].get('email', '') == \
                        legacy_address[
                            'addressLine1']:
                    mapped_types.append(legacy_address['addressTypeId'].lower())
                    email = legacy_address['addressLine1']
                else:
                    folio_address = {}
                    primary = False
                    a += 1
                    for prop in self.user_schema['properties']['personal']['properties']['addresses']['items'][
                        'properties']:
                        if prop in legacy_address:  # is there a match in the csv?
                            if legacy_address[prop].strip():  # Match! Lets report this
                                folio_address[prop] = legacy_address[prop]
                                self.report_legacy_mapping(f"address.{a}.{prop}", True, False)
                                self.report_folio_mapping(f"personal.addresses.{a}.{prop}", True, False)
                            else:  # Match but empty field. Lets report this
                                self.report_legacy_mapping(f"address.{a}.{prop}", True, True)
                                self.report_folio_mapping(f"personal.addresses.{a}.{prop}", True, True)
                        else:
                            self.report_folio_mapping(f"personal.addresses.{a}.{prop}", False, False)
                            self.report_legacy_mapping(f"address.{a}.{prop}", False, False)
                        if str(legacy_address['addressTypeId']).lower() == "temporary":
                            folio_address['addressTypeId'] = "Campus"  # campus
                            if legacy_address['primaryAddress'].lower() == "temporary":
                                primary = True if not primary_set else False
                                primary_set = True
                        elif str(legacy_address['addressTypeId']).lower() == "permanent":
                            if legacy_address['primaryAddress'].lower() == "permanent":
                                primary = True if not primary_set else False
                                primary_set = True
                            folio_address['addressTypeId'] = "Home"  # Home
                        folio_address['primaryAddress'] = primary
                        self.add_to_migration_report("Primary addresses", str(primary))
                        self.add_to_migration_report("Country Codes", folio_address.get('countryId', 'None'))
                    c_id = country_map()[legacy_address['countryId']]
                    if not c_id:
                        self.add_to_migration_report("Unmapped country codes", legacy_address['countryId'] )
                        raise ValueError(f"Wrong country ID {legacy_address['countryId']}")
                    folio_address['countryId'] = c_id
                    folio_user['personal']['addresses'].append(folio_address)

        if not folio_user['personal'].get('email', '').strip() and email:
            folio_user['personal']['email'] = email
            self.add_to_migration_report("Email comes from", "addressLine1")
        else:
            self.add_to_migration_report("Email comes from", "email field")
        if folio_user['personal']['addresses'] and not any(
                a for a in folio_user['personal']['addresses'] if a['primaryAddress']):
            self.add_to_migration_report("Primary addresses", "Unhandled, set first as primary")
            folio_user['personal']['addresses'][0]['primaryAddress'] = True

    def get_users(self, source_file):
        address_fields = ["countryId", "addressLine1", "addressLine2", "city", "region", "postalCode",
                          "addressTypeId", "primaryAddress"]
        csv.register_dialect("tsv", delimiter="\t")
        reader = csv.DictReader(source_file, dialect='tsv')
        current_user = {}
        current_user_id = ""
        for row in reader:
            address = {key: value for (key, value) in row.items() if key in address_fields}
            bad_email = re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", address['addressLine1']) and \
                        address['addressTypeId'].lower() in ['temporary', 'permanent']

            if row['username'] != current_user_id:  # new user, yield the old one.
                old_user = current_user
                first = False if current_user_id else True
                current_user_id = row['username']
                user_data = {key: value for (key, value) in row.items() if key not in address_fields}
                current_user = {"data": user_data,
                                "addresses": [address]}
                if not first:
                    yield old_user
            elif row['username'] == current_user_id and current_user_id:
                if not bad_email:
                    current_user['addresses'].append(address)
                else:
                    self.add_to_migration_report("Emails that are listed as other addresses", bad_email)

    def get_user_group(self, group_code):
        return {"1": "Staff",
                "2": "Faculty",
                "3": "Undergraduate",
                "4": "Graduate",
                "5": "SPEC",
                "6": "Undergraduate",
                "7": "Graduate",
                "8": "Faculty",
                "9": "Library Card",
                "10": "Staff",
                "11": "SPEC(Library Dept Card)",
                "12": "Carrel",
                "13": "Privilege Card (Statutory)",
                "14": "Privilege Card (Statutory)",
                "15": "Proxy Borrower",
                "16": "Faculty",
                "17": "Borrow Direct",
                "18": "Library Card"}.get(group_code, "Unmapped")
