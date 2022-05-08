import ipaddress
import os
import json


def is_ip_private(ip):
    """
    Checking if an ip is private

    :param ip:
    :return:
    """
    return ipaddress.ip_address(ip).is_private


def is_domain_internal(domain):
    """
    Checking if a domain is internal based on provided internal suffixes

    :param domain:
    :return:
    """
    INTERNAL_DOMAIN_SUFFIXES = os.getenv('INTERNAL_DOMAIN_SUFFIXES')
    if not INTERNAL_DOMAIN_SUFFIXES:
        return False
    for suffix in json.loads(INTERNAL_DOMAIN_SUFFIXES):
        if domain.endswith(suffix):
            return True

    return False


def remove_dups(records):
    """
    removing duplicate records by domain name

    :param records:
    :return:
    """
    domains = set()
    new_records = []
    for record in records:
        domains.add(record['name'])
    for domain in domains:
        for record in records:
            if domain == record['name']:
                new_records.append(record)
                break
    return new_records