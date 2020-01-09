import json
import os

import click
import yaml
from yaml import FullLoader

from endpoints import prc


@click.group()
def cli():
    pass


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_file', type=click.File('w'))
@click.option('--description', 'description', default='', help="Description for the policy version")
def generate_rules(input_dir, description, output_file):
    settings = {
        "subconfigs": load_subconfig_settings(input_dir)
    }
    policy = prc.load(settings, description)
    json.dump(policy, output_file)


def load_subconfig_settings(input_dir):
    subconfigs = list()

    click.echo('=> Loading config files')
    for f in sorted(os.listdir(input_dir), reverse=True):
        if f.endswith('.yaml'):
            click.echo('...%s' % f)
            with open(os.path.join(input_dir, f), 'r') as stream:
                subconfigs.append({"name": f.replace('.yaml', ''), **yaml.load(stream, Loader=FullLoader)})

    return subconfigs


if __name__ == '__main__':
    cli()
