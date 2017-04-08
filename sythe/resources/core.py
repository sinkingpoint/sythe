from datetime import datetime
import parsedatetime
import sythe.errors as errors

def filter_resources(resources, condition):
    return [resource for resource in resources if condition.execute(resource)]

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

    def delete(self, args):
        """
        Deletes this resource
        """
        raise NotImplementedError()

    @resource_action(['after'])
    def mark_for_deletion(self, args):
        """
        Marks this resource for deletion after a given period of time.
        If resources continue to match the rule, they are deleted after a time
        """
        if not 'tag:SytheDeletionTime' in self.data:
            cal = parsedatetime.Calendar()
            time_struct, parse_status = cal.parse(args['after'])
            if parse_status == 0:
                raise errors.InvalidArgumentError(
                    'Invalid timespan: {}'.format(args['after'])
                )
            time = datetime(*time_struct[:6])
            self.tag({'key': 'SytheDeletionTime', 'value': str(time.timestamp())})
            self.data['tag:SytheDeletionTime'] = str(time.timestamp())
            self.data['Tags'].append({
                'Key': 'SytheDeletionTime',
                'Value': str(time.timestamp())
            })
        now = datetime.now().timestamp()
        deletion_time = float(self.data['tag:SytheDeletionTime'])

        if now >= deletion_time:
            self.delete(args)
