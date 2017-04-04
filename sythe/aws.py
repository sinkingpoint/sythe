import boto3

def get_ec2_client():
    return boto3.client('ec2')
