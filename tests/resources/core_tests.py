import sythe.parsing.nodes as nodes
import unittest
import sythe.resources.core as resources

class ConditionNodeTests(unittest.TestCase):
    def test_conditions_filter_correctly(self):
        test_resources = [
            {
                'State': {
                    'Name': 'running'
                },
                'tag:Name': 'A Server',
                'Tags':[
                    {
                        'Key': 'Name',
                        'Value': 'A Server'
                    }
                ]
            },
            {
                'State': {
                    'Name': 'running'
                },
                'VpcId': 'vpc-a15f16c4',
                'tag:Name': 'Another Server',
                'Tags':[
                    {
                        'Key': 'Name',
                        'Value': 'Another Server'
                    }
                ]
            }
        ]

        test_cases = [
            (nodes.EqualsNode(nodes.VariableNode('tag:Name'), nodes.StringLiteralNode('"A Server"')), [test_resources[0]]),
            (nodes.EqualsNode(nodes.VariableNode('State.Name'), nodes.StringLiteralNode('"running"')), [test_resources[0], test_resources[1]])
        ]

        for condition, expected in test_cases:
            self.assertEqual(resources.filter_resources(test_resources, condition), expected)
