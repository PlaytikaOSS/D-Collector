import dcollector.utils.utils as utils
import boto3
import os
import json
import uuid


def get_session_by_assume_role(role_arn, session_name, secondary_role_arn=None):
    """
    Returns an AWS session by assuming a provided role.
    Optionally, assumes a secondary role using credentials from the first assumed role.

    :param role_arn: The ARN of the primary role to assume.
    :param session_name: The name for the assumed session.
    :param secondary_role_arn: (Optional) ARN of a secondary role to assume using the credentials of the first.
    :return: boto3.Session with the assumed role credentials.
    """
    # Assume the primary role
    sts_client = boto3.client('sts', 
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                              )
    primary_response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )

    # Extract credentials from the primary role
    credentials = primary_response['Credentials']

    # If a secondary role ARN is provided, assume that role using the primary role's credentials
    if secondary_role_arn:
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        secondary_response = sts_client.assume_role(
            RoleArn=secondary_role_arn,
            RoleSessionName=session_name
        )
        credentials = secondary_response['Credentials']

    # Return a boto3 session using the final credentials
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )


def get_boto(role=None):
    """
    Returns a boto3 Route53 client, optionally assuming a role.

    :param role: (Optional) ARN of a secondary role to assume after assuming the main role.
    :return: boto3 Route53 client or None if an error occurs.
    """
    try:
        if not AWS_ARN:
            # Connecting directly to AWS account
            client = boto3.client(
                "route53",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        else:
            # Assuming role provided to connect to AWS
            session_name = str(uuid.uuid4())
            session = get_session_by_assume_role(AWS_ARN, session_name, secondary_role_arn=role)
            client = session.client("route53")

        return client

    except Exception as error:
        print(f"An error occurred while trying to authenticate to AWS: {error}")
        return None


def is_enabled():
    global AWS_ACCESS_KEY_ID
    global AWS_SECRET_ACCESS_KEY
    global AWS_ARN
    global AWS_ARN_EXTRA_ROLES_FILE
    AWS_ARN_EXTRA_ROLES_FILE = os.getenv('AWS_ARN_EXTRA_ROLES_FILE')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_ARN = os.getenv('AWS_ARN')
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)


def get_domains():
    """
        Pulling all domains from the provider

        :return:
    """
    domains = get_domains_from_client()
    if AWS_ARN_EXTRA_ROLES_FILE:
        try:
            with open(AWS_ARN_EXTRA_ROLES_FILE) as f:
                aws_roles = json.load(f)
        except OSError:
            print(f"Could not open/read file: {AWS_ARN_EXTRA_ROLES_FILE}")
            return domains
        for role in aws_roles:
            domains.extend(get_domains_from_client(role))
    return domains


def get_domains_from_client(role=None):

    if not is_enabled():
        return []

    domains = []

    client = get_boto(role)

    if not client:
        return []

    try:
        hostzone_paginator = client.get_paginator('list_hosted_zones')
        zone_records_paginator = client.get_paginator('list_resource_record_sets')

        hostzone_iterator = hostzone_paginator.paginate()
        for zone_item in hostzone_iterator:
            for hosted_zone in zone_item['HostedZones']:
                zone_records_iterator = zone_records_paginator.paginate(HostedZoneId=hosted_zone['Id'])
                for record_set in zone_records_iterator:
                    for record in record_set['ResourceRecordSets']:
                        # @todo Refactor and generalize.
                        if record['Type'] in ['CNAME', 'A']:
                            domain_data = {
                                'name': record['Name'].rstrip('.').replace('\\052.', '').replace('*.',''),
                                'record_type': record['Type'],
                                'record_value': '',
                                'is_private': False,
                                'source': 'aws'
                            }

                            if 'ResourceRecords' in record:
                                domain_data['record_value'] = record['ResourceRecords'][0]['Value']

                                # check if ip or domain name is private
                                if domain_data['record_type'] == 'A':
                                    domain_data['is_private'] = utils.is_ip_private(domain_data['record_value'])
                                elif domain_data['record_type'] == 'CNAME':
                                    domain_data['is_private'] = utils.is_domain_internal(domain_data['record_value'])

                            domains.append(domain_data)
    except Exception as error:
        print('An error occurred while trying to get aws records:')
        print(str(error))
        return []
    return domains
