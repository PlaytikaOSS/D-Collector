import requests
import os


ZONES_ENDPOINT = "https://api.nsone.net/v1/zones"


def is_enabled():
    global NSONE_TOKEN
    NSONE_TOKEN = os.getenv('NSONE_TOKEN')
    return bool(NSONE_TOKEN)


def get_domains():
    results = set()
    headers = {"X-NSONE-Key": NSONE_TOKEN}
    response = requests.get(ZONES_ENDPOINT, headers=headers)
    response.raise_for_status()
    data = response.json()
    for zone in data:
        zone_name = zone.get("name")
        if not zone_name:
            continue
        results.add(zone_name)
        response = requests.get(ZONES_ENDPOINT + f"/{zone_name}",
                                headers=headers)
        response.raise_for_status()
        sub_domains = response.json().get('records', [])
        for sub_domain in sub_domains:
            domain_name = sub_domain.get("domain")
            if domain_name:
                results.add(domain_name)
    return results
