import sythe.aws
import sythe.errors as errors

def resource_action(required_args):
    def enforce_args(func):
        def wrapper(*args, **kwargs):
            for arg in required_args:
                if not arg in args[1]:
                    raise errors.MissingArgumentError(
                        'Missing argument in {} call: {}'.format(func.__name__, arg)
                    )
            func(*args, **kwargs)
        return wrapper
    return enforce_args

class Resource:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, A):
        if isinstance(A, Resource):
            return A.data == self.data
        return False

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

class EC2Instance(Resource):
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
