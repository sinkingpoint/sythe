import boto3

class Resource:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

class EC2Instance(Resource):
    def __init__(self, data):
        for tag in data['Tags']:
            data['tag:{}'.format(tag['Key'])] = tag['Value']
        Resource.__init__(self, data)

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
    return [EC2Instance(instance) for instance in instances]

def filter_resources(resources, condition):
    return [resource for resource in resources if condition.execute(resource)]
