import os
import dcollector.utils.utils as utils
import re


def is_enabled():
    global DG_TOKEN
    DG_TOKEN = os.getenv('DG_TOKEN')
    return bool(DG_TOKEN)


def get_domains():
    """
    Pulling all domains from the provider

    :return:
    """

    if not is_enabled():
        return []

    import digitalocean

    domains = []

    try:
        manager = digitalocean.Manager(token=DG_TOKEN)
        # Pulling all records from Digital Ocean
        my_domains = manager.get_all_domains()
        for my_domain in my_domains:
            domain = digitalocean.Domain(token=DG_TOKEN, name=my_domain)
            records = domain.get_records()
            for r in records:
                # @todo Refactor and generalize.
                if r.type in ['A', 'CNAME']:
                    domain_data = {
                        'name': do_domain_name_normalise(r),
                        'record_type': r.type,
                        'record_value': r.data,
                        'is_private': False,
                        'source': 'digitalocean'
                    }

                    if domain_data['record_type'] == 'A':
                        domain_data['is_private'] = utils.is_ip_private(domain_data['record_value'])
                    elif domain_data['record_type'] == 'CNAME':
                        domain_data['is_private'] = utils.is_domain_internal(domain_data['record_value'])
                    domains.append(domain_data)
    except Exception as error:
        print('An error occurred while trying to get digital ocean records:')
        print(str(error))
        return []

    return domains


def do_domain_name_normalise(record):
    """
    Removing special characters and formating domain name

    :param record:
    :return:
    """
    # Normalising domain name for Digital Ocean
    name = record.name
    name = name + '.' + record.domain.name
    name = re.sub(r'(\*|@)\.', '', name)
    return name
