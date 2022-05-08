import os
import json

def is_enabled():
    global STATIC_DOMAINS_FILE
    STATIC_DOMAINS_FILE = os.getenv('STATIC_DOMAINS_FILE')
    return bool(STATIC_DOMAINS_FILE)


def get_domains():
    """
    Reading domains from provided file

    :return:
    """

    if not is_enabled():
        return []

    try:
        fr = open(STATIC_DOMAINS_FILE, 'r')
    except IOError:
        print(f'could not read file: {STATIC_DOMAINS_FILE}')
        return []

    return json.load(fr)
