import json

import click
import jsonschema

import akamaiopen
from cloudlets import click_defaults


def load_json(ctx, param, value):
    try:
        ds = json.load(value)
    except ValueError:
        raise click.BadParameter("Invalid JSON file")
    return ds


@click.group()
def cli():
    pass


@cli.command()
@click.argument('json_file', type=click.File('r'), callback=load_json)
@click.option('--schema', 'schema_file', type=click.File(), required=True, help="JSON schema for validation")
def validate_policy(json_file, schema_file):
    click.echo('=> Schema validation... ', nl=False)

    schema = json.load(schema_file)
    jsonschema.validate(json_file, schema)

    click.echo('OK')


@click.command()
@click.option("--policyid", "-pid", help="The policy id for which this operation is performed", required=True)
@click.option("--policy", "-p", type=click.File('r'), help="A file with policy JSON", callback=load_json, required=True)
@click.option("--description", default=None, help="The version description", required=False)
@click_defaults
def update_policy(client_token, client_secret, access_token, host, policyid, policy, description):
    if description:
        policy['description'] = description

    post_url = "/cloudlets/api/v2/policies/{0}/versions?includeRules=false&matchRuleFormat=1.0".format(policyid)
    akamai_session = akamaiopen.OpenClient(host, access_token, client_token, client_secret)
    result = akamai_session.post(post_url, policy)
    if result.status_code != 201:
        raise click.ClickException(result.json()['detail'])
    return result


@click.command()
@click.option("--policyid", "-pid", help="The policy id for which this operation is performed", type=click.INT, required=True)
@click.option("--version", "-v", help="The version to be activated", type=click.INT, required=False)
@click.option("--network", "-net", help="The network where policy will be activated", type=click.Choice(['staging', 'production']), required=True)
@click_defaults
def activate_policy_version(client_token, client_secret, access_token, host, policyid, version, network):
    akamai_session = akamaiopen.OpenClient(host, access_token, client_token, client_secret)

    if version is None:
        get_url = "/cloudlets/api/v2/policies/{0}/versions".format(policyid)
        version = akamai_session.get(get_url).json()[0]['version']

    data = {"network": network}
    post_url = "/cloudlets/api/v2/policies/{0}/versions/{1}/activations".format(policyid, version)
    result = akamai_session.post(post_url, data)
    if result.status_code != 200:
        raise click.ClickException(result.json()['detail'])
    return result
