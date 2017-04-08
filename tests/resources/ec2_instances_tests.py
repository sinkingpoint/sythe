import unittest
from unittest.mock import MagicMock
import sythe.resources.ec2_resources as ec2_resources
import sythe.resources.core as resources

class MockEC2Client:
    """
    A Class which mocks an EC2 client from boto3,
    sending hardcoded pages
    """
    def __init__(self, pages):
        self.pages = pages

    def describe_instances(self, NextToken=0):
        if len(self.pages) == 0:
            return {
                'Reservations': [],
                'NextToken': None
            }

        return {
            'Reservations': [
                {
                    'Instances': self.pages[NextToken]
                }
            ],
            'NextToken': NextToken + 1 if NextToken < len(self.pages) - 1 else None
        }

class GetEC2InstancesTests(unittest.TestCase):
    """
    Tests for the get_ec2_instances method
    """
    def test_get_without_pages(self):
        """
        Tests that it works when there's only one page
        """
        test_cases = [
            [],
            [{'instance-id': 'an instance'}]
        ]

        for instance_page in test_cases:
            client = MockEC2Client([instance_page])
            instances = ec2_resources.get_ec2_instances(client)
            expected_output = [ec2_resources.EC2Instance(item, client) for sublist in [instance_page] for item in sublist]
            self.assertEqual(expected_output, instances)

    def test_get_with_pages(self):
        """
        Tests that it correctly handles the NextToken returned
        with pages
        """
        test_cases = [
            [
                [{'instance-id': 'an instance'}],
                [{'instance-id': 'a second instance'}]
            ]
        ]

        for instance_page in test_cases:
            client = MockEC2Client(instance_page)
            instances = ec2_resources.get_ec2_instances(client)
            expected_output = [ec2_resources.EC2Instance(item, client) for sublist in instance_page for item in sublist]
            self.assertEqual(expected_output, instances)

class EC2InstanceTests(unittest.TestCase):
    def test_augments_correctly(self):
        test_cases = [
            {
                'Tags': [
                    {
                        'Key': 'Test',
                        'Value': 'Test'
                    }
                ]
            },
            {
                'Tags': [
                    {
                        'Key': 'Test2',
                        'Value': 'Test2'
                    },
                    {
                        'Key': 'Test3',
                        'Value': 'Test3'
                    }
                ]
            }
        ]

        for test_case in test_cases:
            instance = ec2_resources.EC2Instance(test_case, None)
            for tag in test_case['Tags']:
                self.assertEqual(instance['tag:{}'.format(tag['Key'])], tag['Value'])

    def test_tag_calls_ec2_tag(self):
        client = MockEC2Client([])
        client.create_tags = MagicMock(return_value=None)
        resource = ec2_resources.EC2Instance(
            {
                'InstanceId': '123',
                'Tags': []
            }, client)
        resource.tag({'key': 'key', 'value': 'value'})
        client.create_tags.assert_called_once_with(
            Resources=['123'],
            Tags=[
                {
                    'Key': 'key',
                    'Value': 'value'
                }
            ]
        )
        self.assertEqual(resource['tag:key'], 'value')

    def test_delete_calls_ec2_delete(self):
        client = MockEC2Client([])
        client.terminate_instances = MagicMock(return_value=None)
        resource = ec2_resources.EC2Instance(
            {
                'InstanceId': '123',
                'Tags': []
            }, client)
        resource.delete({})
        client.terminate_instances.assert_called_once_with(
            InstanceIds=['123']
        )
