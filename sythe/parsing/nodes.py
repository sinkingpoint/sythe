import sythe.parsing.errors as errors

class RuleNode:
    def __init__(self, tokens):
        self.resource = ResourceNode(tokens)

class ResourceNode:
    def __init__(self, tokens):
        valid_resource_types = ['ec2_instance']
        resource = tokens[0]
        if resource in valid_resource_types:
            self.resource_name = resource
            tokens.pop(0)
        else:
            raise errors.ParsingError('Invalid resource type: {}'.format(tokens[0]))

    def get_resource_name(self):
        return self.resource_name


