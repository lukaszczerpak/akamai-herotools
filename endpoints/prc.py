import re

import click

from akamaiopen.cloudlets.PhasedReleaseRule import PhasedReleaseRule, ForwardSettings
from akamaiopen.cloudlets.matches.Match import MatchOperator
from akamaiopen.cloudlets.matches.PathMatch import PathMatch


def parse_record(r):
    pr = PhasedReleaseRule()
    pr.name = r['name']
    pr.forward_settings = ForwardSettings(r['origin'], 100)
    pr.matches.extend(parse_paths(r['path']))

    if 'vanity_path' in r:
        vpr = PhasedReleaseRule()
        vpr.name = 'vanity redirect: %s' % r['name']
        vpr.forward_settings = ForwardSettings('vanity_redirect', 100)
        vpr.matches.extend(parse_paths(r['vanity_path']))
        return [vpr, pr]

    return [pr]


def parse_paths(multi_value):
    positive_values = set()
    negative_values = set()

    for value in multi_value.split(' '):
        if value[0] == '!':
            negative_values.add(value[1:])
        else:
            positive_values.add(value)

    if positive_values:
        value = ' '.join(sorted(positive_values))
        match_operator = MatchOperator.CONTAINS if re.search(r"(^|[^\\])\*", value) else MatchOperator.EQUALS
        yield PathMatch(match_value=value, match_operator=match_operator, negate=False, case_sensitive=False)

    if negative_values:
        value = ' '.join(sorted(negative_values))
        match_operator = MatchOperator.CONTAINS if re.search(r"(^|[^\\])\*", value) else MatchOperator.EQUALS
        yield PathMatch(match_value=value, match_operator=match_operator, negate=True, case_sensitive=False)


def load(settings, description=''):
    click.echo('=> Parsing rules')
    match_rules = []
    for r in settings['subconfigs']:
        click.echo('...%s' % r)
        match_rules.extend([e.to_json() for e in parse_record(r)])

    policy = {
        "description": description,
        "matchRuleFormat": "1.0",
        "matchRules": match_rules
    }

    return policy
