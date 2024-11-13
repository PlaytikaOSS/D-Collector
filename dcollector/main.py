import argparse
import json
import dcollector.providers.gcp as gcp
import dcollector.providers.aws as aws
import dcollector.providers.prisma as prisma
import dcollector.providers.digitalocean as digitalocean
import dcollector.providers.file as local
import dcollector.utils.utils as utils
import dcollector.providers.cycognito as cycognito
import dcollector.providers.cloudflare as cloudflare
import dcollector.providers.ns1 as ns1


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
        digitalocean.get_domains() +
        cycognito.get_domains() +
        cloudflare.get_domains() +
        ns1.get_domains()
    )


def get_enabled_providers():
    """
    Returns status of providers based on environment variables

    :return:
    """
    return {"aws": aws.is_enabled(), "gcp": gcp.is_enabled(), "dg": digitalocean.is_enabled(),
            "prisma": prisma.is_enabled(), "cycognito": cycognito.is_enabled(), "local file": local.is_enabled(),
            "cloudflare": cloudflare.is_enabled(), "ns1": ns1.is_enabled()}


def main(providers):
    """
    Creates a file will all the pulled domains

    :return:
    """

    if providers:
        enabled_providers = get_enabled_providers()
        print("Status of environment variables of providers (True = exists, False = not exists):")
        for provider, provider_status in enabled_providers.items():
            print(f"{provider} : {provider_status}")
        return 0

    # Get records
    domain_list = get_domains()
    
    # save records as json file
    f = open('domains.json', 'w')
    f.write(json.dumps(domain_list))
    print(f' Successfully extracted {len(domain_list)} records')
    return 0


def interactive():
    """
    Getting args from user and passing to main

   :return:
   """
    parser = argparse.ArgumentParser(description='Collect DNS records from various DNS and cloud providers.')
    parser.add_argument('-lp', '--list-providers', help='listing loaded providers', action='store_true',
                        dest="list_providers")
    args = parser.parse_args()
    main(args.list_providers)


if __name__ == '__main__':
    interactive()
