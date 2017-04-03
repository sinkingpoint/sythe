import boto3

def get_ec2_instances(ec2_client=boto3.client('ec2')):
    instances = []
    instance_page = ec2_client.describe_instances()
    instance_from_page = [instance for reservation in instance_page['Reservations']
                          for instance in reservation['Instances']]
    instances = instances + instance_from_page
    while 'NextToken' in instance_page and instance_page['NextToken']:
        instance_page = ec2_client.describe_instances(NextToken=instance_page['NextToken'])
        instance_from_page = [instance for reservation in instance_page['Reservations']
                              for instance in reservation['Instances']]
        instances = instances + instance_from_page
    return [augment_ec2_instance_resource(instance) for instance in instances]

def augment_ec2_instance_resource(resource):
    for tag in resource['Tags']:
        resource['tag:{}'.format(tag['Key'])] = tag['Value']
    return resource

def filter_resources(resources, condition):
    return [resource for resource in resources if condition.execute(resource)]
