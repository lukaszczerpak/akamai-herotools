import os
from urllib.parse import urljoin

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc


class OpenClient:

    def __init__(self, host, access_token, client_token, client_secret):
        self.headers = {
            'Content-Type': 'application/json'
        }

        self.TIMEOUT = 180
        self.session = requests.Session()
        self.session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
            max_body=131072
        )
        self.baseurl = 'https://%s' % host

    @staticmethod
    def from_edgerc(edgerc_path=os.path.join(os.path.expanduser("~"), ".edgerc"), section='default'):
        edgerc = EdgeRc(edgerc_path)
        return OpenClient(edgerc.get(section, 'host'),
                          edgerc.get(section, 'access_token'),
                          edgerc.get(section, 'client_token'),
                          edgerc.get(section, 'client_secret'))

    def get(self, endpoint, headers=None):
        return self.session.get(urljoin(self.baseurl, endpoint),
                                headers=headers, timeout=self.TIMEOUT)

    def delete(self, endpoint, headers=None):
        return self.session.delete(urljoin(self.baseurl, endpoint),
                                   headers=headers, timeout=self.TIMEOUT)

    def post(self, endpoint, data, headers=None):
        return self.session.post(urljoin(self.baseurl, endpoint), json=data,
                                 headers={**self.headers, **headers} if headers else self.headers, timeout=self.TIMEOUT)

    def put(self, endpoint, data, headers=None):
        return self.session.put(urljoin(self.baseurl, endpoint), json=data,
                                headers={**self.headers, **headers} if headers else self.headers, timeout=self.TIMEOUT)
