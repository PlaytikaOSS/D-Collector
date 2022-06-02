import os
import dcollector.utils.utils as utils
import requests
import json


def get_rql():
    """
    Returns configuration for prisma to fetch aws records

    :return:
    """
    return {
        'aws': {
            'dns': '''config from cloud.resource where api.name = 'aws-route53-list-hosted-zones' ''',
        }
    }


def get_prisma_token():
    """
    Returns session token from prisma

    :return:
    """
    headers = {
        'Accept': 'application/json; charset=UTF-8',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    url = f'{PRISMA_URL}/login'
    body = {
        'username': PRISMA_API_KEYID,
        'password': PRISMA_API_SECRET
    }
    try:
        resp = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)
    except Exception as error:
        print('An error occurred while trying to get prisma token:')
        print(str(error))
        return ""
    return resp.json()['token']


def get_prisma_config(query):
    """
    Returns DNS records from prisma

    :param query:
    :return:
    """
    headers = {
        'Accept': 'application/json; charset=UTF-8',
        'Content-Type': 'application/json; charset=UTF-8',
        'x-redlock-auth': get_prisma_token()
    }
    url = f'{PRISMA_URL}/search/config'
    body = {
        'withResourceJson': True,
        'query': query
    }
    try:
        resp = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)
    except Exception as error:
        print('An error occurred while trying to get prisma config:')
        print(str(error))
        return ""
    return resp.json()['data']


def is_enabled():
    global PRISMA_API_SECRET
    global PRISMA_API_KEYID
    global PRISMA_URL
    PRISMA_API_SECRET = os.getenv('PRISMA_API_SECRET')
    PRISMA_API_KEYID = os.getenv('PRISMA_API_KEYID')
    PRISMA_URL = os.getenv('PRISMA_URL')
    return bool(PRISMA_URL and PRISMA_API_KEYID and PRISMA_API_SECRET)


def get_domains():
    """
    Pulling all domains from the provider

    :return:
    """
    if not is_enabled():
        return []

    rql = get_rql()
    data = get_prisma_config(rql['aws']['dns'])

    if not data:
        return []

    domains = []

    for zone in data['items']:
        for record in zone['data']['resourceRecordSet']:
            # @todo Refactor and generalize.
            if record['type'] in ['CNAME', 'A']:
                domain_data = {
                    'name': record['name'].rstrip('.').replace('\\052.', ''),
                    'record_type': record['type'],
                    'record_value': '',
                    'is_private': False,
                    'source': 'prisma'
                }

                if len(record['resourceRecords']):
                    domain_data['record_value'] = record['resourceRecords'][0]['value']

                    # Check if ip or domain name is private
                    if record['type'] == 'A':
                        domain_data['is_private'] = utils.is_ip_private(domain_data['record_value'])
                    elif record['type'] == 'CNAME':
                        domain_data['is_private'] = utils.is_domain_internal(domain_data['record_value'])

                domains.append(domain_data)
    return domains
