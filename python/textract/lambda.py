import boto3
import time

def start_job(aws_client, s3_bucket, object_name):
    """Starts textraction job
    aws_client: Boto3 Textraction client
    s3_bucket: Bucket name where the object is location
    object_name: Object name of what will be analyzed

    return: The job ID for the Textraction task
    """
    response = None
    response = aws_client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': object_name
    }})
    return response['JobId']

def is_job_complete(aws_client, job_id):
    """Returns status of Textraction client job
    aws_client: Boto3 Textraction client
    job_id: Textraction job ID to be valdiated

    returns: Boolean, True if job is complete
    """
    time.sleep(5)
    response = aws_client.get_document_text_detection(JobId = job_id)
    status = response['JobStatus']
    print("Job status: {}".format(status))

    while status == 'IN_PROGRESS':
        time.sleep(5)
        response = aws_client.get_document_text_detection(JobId = job_id)
        status = response['JobStatus']
        print("Job status: {}".format(status))
    
    return True

def get_job_results(aws_client, job_id):
    """Returns status of Textraction client job
    aws_client: Boto3 Textraction client
    job_id: Textraction job ID to be valdiated

    returns: Job results
    """
    time.sleep(5)
    response = aws_client.get_document_text_detection(JobId=job_id)

    return response

if __name__ == "__main__":
    # Document
    s3_bucket = "AWS_BUCKET"
    document_name = "DOCUMENT_TO_SEARCH"
    client = boto3.client('textract', 
        aws_access_key_id='ACCESS_KEY',
        aws_secret_access_key='SECRET_ACCESS_KEY',
        region_name = 'us-east-1')

    job_id = start_job(client, s3_bucket, document_name)
    print("Started job with id: {}".format(job_id))
    time.sleep(5)
    if is_job_complete(client, job_id):
        response = get_job_results(client, job_id)
        # Print detected text
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                print('\033[94m' + item["Text"] + '\033[0m')
