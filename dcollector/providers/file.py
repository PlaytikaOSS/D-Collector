from dcollector.config import STATIC_DOMAINS_FILE
import json


def get_domains():
    """
    Reading domains from provided file

    :return:
    """
    if not STATIC_DOMAINS_FILE:
        return []

    try:
        fr = open(STATIC_DOMAINS_FILE, 'r')
    except IOError:
        print(f'could not read file: {STATIC_DOMAINS_FILE}')
        return []

    return json.load(fr)
