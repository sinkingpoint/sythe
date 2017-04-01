import unittest
import sythe.resources as resources

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
            instances = resources.get_ec2_instances(MockEC2Client([instance_page]))
            self.assertEqual(instance_page, instances)

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
            instances = resources.get_ec2_instances(MockEC2Client(instance_page))
            self.assertEqual([item for sublist in instance_page for item in sublist], instances)
