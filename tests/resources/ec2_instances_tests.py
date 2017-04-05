import unittest
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
            instances = ec2_resources.get_ec2_instances(MockEC2Client([instance_page]))
            expected_output = [ec2_resources.EC2Instance(item) for sublist in [instance_page] for item in sublist]
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
            instances = ec2_resources.get_ec2_instances(MockEC2Client(instance_page))
            expected_output = [ec2_resources.EC2Instance(item) for sublist in instance_page for item in sublist]
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
            instance = ec2_resources.EC2Instance(test_case)
            for tag in test_case['Tags']:
                self.assertEqual(instance['tag:{}'.format(tag['Key'])], tag['Value'])
