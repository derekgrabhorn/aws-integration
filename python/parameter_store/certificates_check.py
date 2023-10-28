import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend

ssm_client = boto3.client('ssm')

FILTER_STRING = ".cert.pem"
WARNING_DAYS = 10

def get_parameter_value(param_name):
    try:
        response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
        param_value = response['Parameter']['Value']

        return param_value
    
    except ClientError as error:
        print(f"Error occurred: {error}")
        return None

def decode_certificate(certificate_data):
    certificate = x509.load_pem_x509_certificate(certificate_data, default_backend())
    return certificate

def expiration_check(cert, warning_days):
    now = datetime.utcnow()
    time_remaining = cert.not_valid_after - now

    if time_remaining.days < warning_days:
        print(f"\nWARNING! Certificate {cert.subject} has {time_remaining.days} days left until expiration!\n")

def process_certs(list_of_certificates):
    for certificate in list_of_certificates:

        # Get string value of Parameter
        cert_data = get_parameter_value(certificate['Name'])

        # Encode because it needs to be read as bytes
        cert_data_bytes = cert_data.encode('utf-8')

        decoded_cert = decode_certificate(cert_data_bytes)

        expiration_check(decoded_cert, WARNING_DAYS)

def find_certs(file_extension_filter):
    paginator = ssm_client.get_paginator('describe_parameters')

    parameter_filters = [
        {
            'Key': 'Name',
            'Option': 'Contains',
            'Values': [file_extension_filter]
        }
    ]

    filtered_parameters = []

    try:
        for page in paginator.paginate(ParameterFilters=parameter_filters):
            for parameter in page['Parameters']:
                filtered_parameters.append(parameter)
        return filtered_parameters

    except ClientError as error:
        print(f"Error occurred: {error}")
        return []

if __name__ == "__main__":
    certs_list = find_certs(FILTER_STRING)
    process_certs(certs_list)