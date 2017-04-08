import unittest
from unittest.mock import MagicMock
import sythe.resources.core as resources
import sythe.parsing.nodes as nodes
from sythe.errors import InvalidArgumentError
from sythe.errors import MissingArgumentError

class ResourceActionTests(unittest.TestCase):
    def test_resource_action_calls_when_allowed(self):
        @resources.resource_action(['A', 'B'])
        def method(self, args): return '123'
        self.assertEqual('123', method(None, {'A': 'A', 'B': 'B'}))

    def test_resource_action_fails_on_invalid_args(self):
        @resources.resource_action(['A', 'B'])
        def method(self, args): return '123'
        with self.assertRaises(MissingArgumentError):
            method(None, {'A': 'A'})


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

class ResourceTests(unittest.TestCase):
    def test_get_item_gets(self):
        resource_values = {'A': 'A', 'B': 'B'}
        resource = resources.Resource(resource_values, None)
        for key, value in resource_values.items():
            self.assertEqual(resource[key], value)
            self.assertTrue(key in resource)

    def test_mark_for_deletion_marks(self):
        resource = resources.Resource({'Tags':[]}, None)
        test_cases = [
            '1 minute',
            '5 minutes, 3 seconds',
            '1 hour, 90 seconds, 3 hours',
            '1 day, 3 seconds',
            '1 month, 50 days'
        ]
        for duration in test_cases:
            resource.tag = MagicMock()
            resource.mark_for_deletion({'after': duration})
            resource.tag.assert_called_once()

    def test_mark_for_deletion_deletes(self):
        resource = resources.Resource({'Tags':[]}, None)
        resource.tag = MagicMock()
        resource.delete = MagicMock()
        resource.mark_for_deletion({'after': '0 seconds'})
        resource.tag.assert_called_once()
        resource.delete.assert_called_once()

    def test_mark_for_deletion_fails_on_invalid_duration(self):
        resource = resources.Resource({'Tags':[]}, None)
        resource.tag = MagicMock()
        resource.delete = MagicMock()
        test_cases = [
            'cats',
            '0 flerbles',
            '3 hors'
        ]

        for duration in test_cases:
            with self.assertRaises(InvalidArgumentError):
                resource.mark_for_deletion({'after': duration})


