import requests
import os
import dcollector.utils.utils as utils


ZONES_ENDPOINT = "https://api.cloudflare.com/client/v4/zones"
DOMAINS_ENDPOINT = "https://api.cloudflare.com/client/v4/zones/{}/dns_records"


def is_enabled():
    global CLOUDFLARE_TOKEN
    global CLOUDFLARE_ACCOUNT_ID
    CLOUDFLARE_TOKEN = os.getenv('CLOUDFLARE_TOKEN')
    CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    return bool(CLOUDFLARE_TOKEN and CLOUDFLARE_ACCOUNT_ID)


def get_domains():
    if not is_enabled():
        return []

    results = []
    headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
               "Accept": "application/json"}
    response = requests.get(ZONES_ENDPOINT,
                            headers=headers,
                            params={"account.id": CLOUDFLARE_ACCOUNT_ID})
    response.raise_for_status()
    data = response.json()
    for zone in data.get("result", []):
        zone_id = zone.get("id")
        response = requests.get(DOMAINS_ENDPOINT.format(zone_id),
                                headers=headers)
        response.raise_for_status()
        sub_domains = response.json().get('result', [])
        for sub_domain in sub_domains:
            record_type = sub_domain.get('type')
            record_value = sub_domain.get('content')
            if record_type in ["A", "AAAA"]:
                is_private = utils.is_ip_private(record_value)
            elif record_type == "CNAME":
                is_private = utils.is_domain_internal(record_value)
            else:
                continue
            domain_data = {
                'name': sub_domain.get('name').rstrip('.').replace('\\052.', '').replace('*.', ''),
                'record_type': record_type,
                'record_value': record_value,
                'is_private': is_private,
                'source': 'cloudflare'
            }
            results.append(domain_data)
    return results
