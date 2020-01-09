from functools import wraps

import click


def click_defaults(func):
    @wraps(func)
    @click.option("--client-token", envvar='AKAMAI_CLIENT_TOKEN',
                  required=True, help="Akamai Client Token. Default is to use AKAMAI_CLIENT_TOKEN from environment")
    @click.option("--client-secret", envvar='AKAMAI_CLIENT_SECRET',
                  required=True, help="Akamai Client Secret. Default is to use AKAMAI_CLIENT_SECRET from environment")
    @click.option("--access-token", envvar='AKAMAI_ACCESS_TOKEN',
                  required=True, help="Akamai Access Token. Default is to use AKAMAI_ACCESS_TOKEN from environment")
    @click.option("--host", envvar='AKAMAI_HOST',
                  required=True, help="Akamai Host. Default is to use AKAMAI_HOST from environment")
    def _wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return _wrapped
