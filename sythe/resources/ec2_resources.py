from sythe.resources.core import Resource
from sythe.resources.core import resource_action
from sythe.registry import resource_registry
from sythe.aws import get_ec2_client

@resource_registry.register('ec2_instance')
class EC2Instance(Resource):
    """
    A resource for an instance in EC2.
    """
    def __init__(self, data, client):
        if 'Tags' in data:
            for tag in data['Tags']:
                data['tag:{}'.format(tag['Key'])] = tag['Value']
        Resource.__init__(self, data, client)

    @resource_action(['key', 'value'])
    def tag(self, args):
        key = args['key']
        value = args['value']
        self.client.create_tags(
            Resources=[self.data['InstanceId']],
            Tags=[{'Key': key, 'Value': value}]
        )
        self.data['tag:{}'.format(key)] = value
        self.data['Tags'].append({
            'Key': key,
            'Value': value
        })

    @resource_action([])
    def delete(self, args):
        self.client.terminate_instances(InstanceIds=[self.data['InstanceId']])

def get_ec2_instances(ec2_client=get_ec2_client()):
    """
    Gets all the EC2 instances using the configuration from a given
    ec2 client. Handles pagination basically.
    """
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
    return [EC2Instance(instance, ec2_client) for instance in instances]
