import sys
import requests
import os

NUM_OF_PAGES = 10
NUM_OF_ITEMS = 10000
URL_PREFIX = "https://api.platform.cycognito.com/v0"


# asset_type = ip / domain / cert
# data = '[{"op":"in","field":"security-rating","values":["A"]}]'
def get_object_paginated(asset_type, pagination):
    offset = 0
    while offset < NUM_OF_PAGES:
        res = requests.post(
            f"{URL_PREFIX}/{CY_REALM}/assets/{asset_type}",
            params={"key": CY_KEY, "count": pagination, "offset": offset},
            headers={"Content-Type": "application/frdy+json", "Accept": "application/frdy+json"},
        )
        res.raise_for_status()
        res = res.json()
        if not res:
            break
        yield from res
        offset = offset + 1


def is_enabled():
    global CY_KEY
    global CY_REALM
    CY_KEY = os.getenv('CY_KEY')
    CY_REALM = os.getenv('CY_REALM')
    return bool(CY_KEY and CY_REALM)


def get_domains():
    if not is_enabled():
        return []

    domains = []

    all = list(get_object_paginated('domain', NUM_OF_ITEMS))
    for asset in all:
        for ip in asset['ip-names']:
            domain_data = {
                'name': asset['domain'].rstrip('.').replace('\\052.', '').replace('*.', ''),
                'record_type': 'A',
                'record_value': ip,
                'is_private': False,
                'source': 'cycognito'
            }
            domains.append(domain_data)
    return domains


