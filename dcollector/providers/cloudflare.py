import requests
import os


ZONES_ENDPOINT = "https://api.cloudflare.com/client/v4/zones"
DOMAINS_ENDPOINT = "https://api.cloudflare.com/client/v4/zones/{}/dns_records"


def is_enabled():
    global CLOUDFLARE_TOKEN
    global CLOUDFLARE_ACCOUNT_ID
    CLOUDFLARE_TOKEN = os.getenv('CLOUDFLARE_TOKEN')
    CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    return bool(CLOUDFLARE_TOKEN and CLOUDFLARE_ACCOUNT_ID)


def get_domains():
    results = []
    headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
               "Accept": "application/json"}
    response = requests.get(ZONES_ENDPOINT,
                            headers=headers,
                            params={"account.id": CLOUDFLARE_ACCOUNT_ID})
    response.raise_for_status()
    data = response.json()
    for zone in data.get("result", []):
        results.append(zone.get("name"))
        zone_id = zone.get("id")
        response = requests.get(DOMAINS_ENDPOINT.format(zone_id),
                                headers=headers)
        response.raise_for_status()
        sub_domains = response.json().get('result', [])
        for sub_domain in sub_domains:
            try:
                results.append(sub_domain.get("name"))
            except KeyError:
                print(sub_domain)
    return results
