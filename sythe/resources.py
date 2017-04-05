"""
This module defines resources which can be used in sythe.
Resources are objects that contain metadata and define a number of actions
that can be defined across that resource
"""

from datetime import datetime
import parsedatetime
import sythe.aws
import sythe.errors as errors

def resource_action(required_args):
    """
    A decorator which enforces that the args dict passed to an
    action contains the required arguments
    """
    def enforce_args(func):
        """Returns a decorator that enforces the given args exist"""
        def wrapper(*args, **kwargs):
            """
            Raises a MissingArgumentError if any of the required arguments
            are missing in the given args dict
            """
            for arg in required_args:
                if not arg in args[1]:
                    raise errors.MissingArgumentError(
                        'Missing argument in {} call: {}'.format(func.__name__, arg)
                    )
            func(*args, **kwargs)
        return wrapper
    return enforce_args

class Resource(object):
    """
    A Base Resource class which is the parent class of all resources that
    we can define rules over. Defines a number of default actions.
    """
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, other):
        if isinstance(other, Resource):
            return other.data == self.data
        return False

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def tag(self, args):
        """
        Adds a tag to this resource using the given
        `key` and `value` args
        """
        raise NotImplementedError()

    @resource_action(['after'])
    def mark_for_deletion(self, args):
        """
        Marks this resource for deletion after a given period of time.
        If resources continue to match the rule, they are deleted after a time
        """
        cal = parsedatetime.Calendar()
        time_struct, parse_status = cal.parse(args['after'])
        if parse_status == 0:
            raise errors.InvalidArgumentError(
                'Invalid timespan: {}'.format(args['after'])
            )
        time = datetime(*time_struct[:6])
        self.tag({'key': 'SytheDeletionTime', 'value': str(time.timestamp())})

class EC2Instance(Resource):
    """
    A resource for an instance in EC2.
    """
    def __init__(self, data):
        if 'Tags' in data:
            for tag in data['Tags']:
                data['tag:{}'.format(tag['Key'])] = tag['Value']
        Resource.__init__(self, data)

    @resource_action(['key', 'value'])
    def tag(self, args):
        ec2_client = sythe.aws.get_ec2_client()
        ec2_client.create_tags(
            Resources=[self.data['InstanceId']],
            Tags=[{'Key': args['key'], 'Value': args['value']}]
        )

def get_ec2_instances(ec2_client=sythe.aws.get_ec2_client()):
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
    return [EC2Instance(instance) for instance in instances]

def filter_resources(resources, condition):
    return [resource for resource in resources if condition.execute(resource)]
