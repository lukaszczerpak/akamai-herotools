import logging
import re

import click
from jsonpath_ng.ext import parse

from akau import click_defaults
from akau import LabSupport
from akau.sleep_util import animated_random_sleep


def validate_user_id(ctx, param, value):
    if not re.match(r"^[a-z0-9]+$", value):
        raise click.BadParameter('user id must be alphanumeric')
    if len(value) < 4:
        raise click.BadParameter('user id must be at least 4 characters long')
    if len(value) > 12:
        raise click.BadParameter('user id cannot be longer than 12 characters')
    return value


def wait():
    animated_random_sleep(1, 10)


@click.command()
@click.argument('user-id', callback=validate_user_id)
@click_defaults
def setup_lab(client_token, client_secret, access_token, host, user_id):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    lab_support = LabSupport(host, access_token, client_token, client_secret)
    policy_name = lab_support.get_policy_name(user_id)
    config_name = lab_support.get_config_name(user_id)

    # get list of policies for given user_id
    found = [p for p in lab_support.get_policy_list() if p['name'] == policy_name]
    if not found:
        # create new policy
        wait()
        policy_id = lab_support.create_policy(user_id)
    else:
        policy_id = found[0]['policyId']

    # get list of configs for given user_id
    wait()
    found = [p for p in lab_support.get_config_list() if p['propertyName'] == config_name]
    if not found:
        # clone from template
        wait()
        property_id, property_version = lab_support.new_config(user_id)
        property_active = False
    else:
        property_id = found[0]['propertyId']
        property_version = found[0]['latestVersion']
        property_active = True if found[0]['stagingVersion'] else False

    if not property_active:
        # get config
        wait()
        rules = lab_support.get_config(property_id, property_version)

        # update policy
        cloudlet_behavior = parse("$..children[?(@.name=='ENDPOINTS - init')]..behaviors[?(@.name=='phasedRelease')].options").find(rules)[0].value
        cloudlet_behavior['cloudletPolicy']['id'] = policy_id
        cloudlet_behavior['cloudletPolicy']['name'] = policy_name

        # update config
        wait()
        lab_support.update_config(property_id, property_version, rules)

        # update hostnames
        wait()
        lab_support.update_hostname(property_id, property_version, user_id)

        # activate
        wait()
        lab_support.activate_config(property_id, property_version)

    click.echo(f"\n{'-' * 80}\n")
    click.echo(f"  YOUR INDIVIDUAL POLICY: {policy_id}")
    click.echo(f"YOUR INDIVIDUAL HOSTNAME: {lab_support.get_hostname(user_id)}")
    click.echo(f"\n{'-' * 80}\n")
