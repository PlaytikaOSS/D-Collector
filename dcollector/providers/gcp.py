import os
import dcollector.utils.utils as utils


def is_enabled():
    global GCP_PRIVATE_KEY_FILE
    global GCP_PROJECT
    GCP_PRIVATE_KEY_FILE = os.getenv('GCP_PRIVATE_KEY_FILE')
    GCP_PROJECT = os.getenv('GCP_PROJECT')
    return bool(GCP_PROJECT and GCP_PRIVATE_KEY_FILE)

def get_domains():
    """
    Pulling all domains from the provider

    :return:
    """
    if not is_enabled():
        return []

    from googleapiclient import discovery
    from google.oauth2 import service_account

    try:
        gcp_credentials = service_account.Credentials.from_service_account_file(GCP_PRIVATE_KEY_FILE)
    except Exception as error:
        print(f'Could not read file: {GCP_PRIVATE_KEY_FILE}')
        print(str(error))
        return []

    try:
        service = discovery.build('dns', 'v1', credentials=gcp_credentials)

        # Identifies the project addressed by this request.
        project = GCP_PROJECT

        domains = []
        request = service.managedZones().list(project=project)
        # Pulling all records from the GCP project
        while request is not None:
            response = request.execute()
            for managed_zone in response['managedZones']:
                request_record = service.resourceRecordSets().list(project=project, managedZone=managed_zone['id'])
                while request_record is not None:
                    response_record = request_record.execute()
                    for resource_record_set in response_record['rrsets']:
                        if resource_record_set['type'] in ['A','CNAME']:
                            domain_data = {
                                'name': resource_record_set['name'].rstrip('.').replace('\\052.', '').replace('*.',''),
                                'record_type': resource_record_set['type'],
                                'record_value': resource_record_set['rrdatas'][0],
                                'is_private': False,
                                'source': 'gcp'
                            }

                            # Check if ip or domain name is private
                            if domain_data['record_type'] == 'A':
                                domain_data['is_private'] = utils.is_ip_private(domain_data['record_value'])
                            elif domain_data['record_type'] == 'CNAME':
                                domain_data['is_private'] = utils.is_domain_internal(domain_data['record_value'])

                            domains.append(domain_data)
                    request_record = service.resourceRecordSets().list_next(previous_request=request_record,
                                                                            previous_response=response_record)
            request = service.managedZones().list_next(previous_request=request, previous_response=response)
    except Exception as error:
        print('An error occurred while trying to get gcp records:')
        print(str(error))
        return []

    return domains
