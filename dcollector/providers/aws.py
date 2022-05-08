import dcollector.utils.utils as utils
import boto3
import os


def get_session_by_assume_role(role_arn, session_name):
    """
    Returns AWS session by assuming a provided role

    :param role_arn:
    :param session_name:
    :return:
    """
    client = boto3.client('sts',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
    session = boto3.Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                            aws_session_token=response['Credentials']['SessionToken'])
    return session


def get_boto():
    """
    Returns boto client from aws

    :return:
    """
    import uuid
    try:
        if not AWS_ARN:
            # Connecting directly to AWS account
            client = boto3.client(
                'route53',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        else:
            # Assuming role provided to connect to AWS
            session_name = str(uuid.uuid4())
            session = get_session_by_assume_role(AWS_ARN, session_name)
            client = session.client('route53')
    except Exception as error:
        print('An error occurred while trying to authenticate to aws:')
        print(str(error))
        return ""

    return client


def is_enabled():
    global AWS_ACCESS_KEY_ID
    global AWS_SECRET_ACCESS_KEY
    global AWS_ARN
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_ARN = os.getenv('AWS_ARN')
    return bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)


def get_domains():
    """
    Pulling all domains from the provider

    :return:
    """

    if not is_enabled():
        return []

    domains = []

    client = get_boto()

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
                                'is_private': False
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
