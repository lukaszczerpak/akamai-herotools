import json
import logging
import re
from functools import wraps

import click

import akamaiopen

CONTRACT_ID = "ctr_C-1ED34DY"
GROUP_ID = "grp_157214"
GROUP_ID_INT = 157214
PRODUCT_ID = "SPM"
CLOUDLET_ID = 7
TEMPLATE_PRP_ID = "prp_586668"
TEMPLATE_PRP_VER = 1
DOMAIN = "labstep.dance"
EH_NAME = "hero.akademo.it.edgesuite.net"
EH_ID = "ehn_4928729"


def click_defaults(func):
    @wraps(func)
    @click.option("--client-token", envvar='AKAMAI_CLIENT_TOKEN', required=True)
    @click.option("--client-secret", envvar='AKAMAI_CLIENT_SECRET', required=True)
    @click.option("--access-token", envvar='AKAMAI_ACCESS_TOKEN', required=True)
    @click.option("--host", envvar='AKAMAI_HOST', required=True)
    def _wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return _wrapped


class LabSupport(object):

    def __init__(self, host, access_token, client_token, client_secret):
        self.akamai_session = akamaiopen.OpenClient(host, access_token, client_token, client_secret)

    def get_policy_name(self, user_id):
        return f"hero_{user_id}"

    def get_config_name(self, user_id):
        return f"hero_{user_id}"

    def get_hostname(self, user_id):
        return f"{user_id}.{DOMAIN}"

    def get_policy_list(self):
        url = f"/cloudlets/api/v2/policies?gid={GROUP_ID_INT}&cloudletId={CLOUDLET_ID}"
        logging.info('=> fetching list of policies')
        result = self.akamai_session.get(url)
        if result.status_code != 200:
            raise click.ClickException(result.json())
        return result.json()

    def create_policy(self, user_id):
        policy_name = self.get_policy_name(user_id)
        data = {
            "cloudletId": CLOUDLET_ID,
            "description": "SA2020 From Zero To Hero lab",
            "groupId": GROUP_ID_INT,
            "name": policy_name
        }

        logging.info(f"=> creating policy with name '{policy_name}'")
        result = self.akamai_session.post('/cloudlets/api/v2/policies', data)
        if result.status_code == 201:
            pid = result.json()['policyId']
            logging.info(f'.. done (id={pid})')
        else:
            raise click.ClickException(result.json())

        return pid

    def get_config_list(self):
        url = f"/papi/v1/properties?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        logging.info(f'=> fetching list of configs')
        result = self.akamai_session.get(url)
        if result.status_code != 200:
            raise click.ClickException(result.json())

        return result.json()['properties']['items']

    def new_config(self, user_id):
        config_name = self.get_config_name(user_id)
        url = f"/papi/v1/properties?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        data = {
            "productId": PRODUCT_ID,
            "propertyName": config_name,
            "cloneFrom": {
                "propertyId": TEMPLATE_PRP_ID,
                "version": TEMPLATE_PRP_VER,
                "copyHostnames": False
            }
        }

        logging.info(f"=> creating new property with name '{config_name}'")
        result = self.akamai_session.post(url, data)
        if result.status_code == 201:
            pid = re.match(r".*/properties/(prp_[0-9]+)\\?.*", result.json().get('propertyLink')).group(1)
            pv = 1
            logging.info(f'.. done (id={pid}, version={pv})')
        else:
            raise click.ClickException(result.json())

        return pid, pv

    def get_config(self, property_id, property_version):
        headers = {
            'Accept': 'application/vnd.akamai.papirules.v2019-07-25+json'
        }
        url = f"/papi/v1/properties/{property_id}/versions/{property_version}/rules?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        logging.info(f'=> fetching property id={property_id}, version={property_version}')
        result = self.akamai_session.get(url, headers)

        return result.json()

    def update_config(self, property_id, property_version, json_data):
        headers = {
            'Content-Type': 'application/vnd.akamai.papirules.v2019-07-25+json'
        }
        url = f"/papi/v1/properties/{property_id}/versions/{property_version}/rules?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        logging.info(f'=> updating property id={property_id}, version={property_version}')
        result = self.akamai_session.put(url, json_data, headers)

        if result.status_code != 200:
            raise click.ClickException(result.json())

        logging.info(f'.. done')
        return result.json()

    def update_hostname(self, property_id, property_version, user_id):
        url = f"/papi/v1/properties/{property_id}/versions/{property_version}/hostnames?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        data = [
            {
                "cnameFrom": self.get_hostname(user_id),
                "cnameTo": EH_NAME,
                "cnameType": "EDGE_HOSTNAME",
                "edgeHostnameId": EH_ID
            }
        ]
        logging.info(f'=> updating hostname')
        result = self.akamai_session.put(url, data)

        if result.status_code != 200:
            raise click.ClickException(result.json())

        logging.info(f'.. done')
        return result.json()

    def activate_config(self, property_id, property_version):
        url = f"/papi/v1/properties/{property_id}/activations?contractId={CONTRACT_ID}&groupId={GROUP_ID}"
        data = {
            "propertyVersion": property_version,
            "network": "STAGING",
            "note": "automated activation",
            "useFastFallback": False,
            "notifyEmails": [
                "lczerpak@akamai.com"
            ]
        }
        logging.info(f'=> activating property id={property_id}, version={property_version}')
        result = self.akamai_session.post(url, data)
        if result.status_code == 400 and "warnings-not-acknowledged" in result.text:
            data["acknowledgeWarnings"] = [warning['messageId'] for warning in result.json()['warnings']]
            logging.info(f'.. acknowledging warnings')
            result = self.akamai_session.post(url, data)

        if result.status_code != 201:
            raise click.ClickException(result.json())

        logging.info(f'.. submitted (will take approx. 10min)')
        return result.json()
