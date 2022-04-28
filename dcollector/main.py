import argparse
import json
import dcollector.providers.gcp as gcp
import dcollector.providers.aws as aws
import dcollector.providers.prisma as prisma
import dcollector.providers.digitalocean as digitalocean
import dcollector.providers.file as local
import dcollector.utils.utils as utils


def get_domains():
    """
    Pulls domains from the relevant providers and remove dups

    :return:
    """

    return utils.remove_dups(
        aws.get_domains() +
        gcp.get_domains() +
        local.get_domains() +
        prisma.get_domains() +
        digitalocean.get_domains()
    )


def main():
    """
    Creates a file will all the pulled domains

    :return:
    """
    parser = argparse.ArgumentParser(description='Collect DNS records from various DNS and cloud providers.')
    args = parser.parse_args()

    # Get records
    domain_list = get_domains()
    
    # save records as json file
    f = open('domains.json', 'w')
    f.write(json.dumps(domain_list))
    print(f' Successfully extracted {len(domain_list)} records')
    return 0


if __name__ == '__main__':
    main()
