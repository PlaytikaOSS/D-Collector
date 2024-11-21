import requests
import os
import dcollector.utils.utils as utils


ZONES_ENDPOINT = "https://api.nsone.net/v1/zones"


def is_enabled():
    global NSONE_TOKEN
    NSONE_TOKEN = os.getenv('NSONE_TOKEN')
    return bool(NSONE_TOKEN)


def get_domains():
    if not is_enabled():
        return []

    results = []
    headers = {"X-NSONE-Key": NSONE_TOKEN}
    response = requests.get(ZONES_ENDPOINT, headers=headers)
    response.raise_for_status()
    data = response.json()
    for zone in data:
        zone_name = zone.get("name")
        if not zone_name:
            continue
        response = requests.get(ZONES_ENDPOINT + f"/{zone_name}",
                                headers=headers)
        response.raise_for_status()
        sub_domains = response.json().get('records', [])
        for sub_domain in sub_domains:
            domain_name = sub_domain.get("domain")
            if domain_name:
                record_type = sub_domain.get('type')
                record_value = sub_domain.get('short_answers')
                if record_type in ["A", "AAAA"]:
                    is_private = any([utils.is_ip_private(ip) for ip in record_value])
                elif record_type == "CNAME":
                    is_private = utils.is_domain_internal(record_value)
                else:
                    continue
                for record in record_value:
                    domain_data = {
                        'name': domain_name.rstrip('.').replace('\\052.', '').replace('*.', ''),
                        'record_type': record_type,
                        'record_value': record,
                        'is_private': is_private,
                        'source': 'NS1'
                    }
                    results.append(domain_data)
    return results
