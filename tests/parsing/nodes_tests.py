import unittest
import sythe.parsing.nodes as nodes
import sythe.parsing.errors as errors

class RuleNodeTests(unittest.TestCase):
    """
    Tests for confirming the behaviour of the RuleNode class
    which is the top level node in this parser
    """
    def test_no_open_paren_fails(self):
        """
        Tests that parsing fails if the resource is not followed by an open parenthesis
        """
        test_cases = [
            ['ec2_instance'],
            ['ec2_instance', '{'],
            ['ec2_instance', ')']
        ]

        for test_case in test_cases:
            with self.assertRaises(errors.ParsingError):
                nodes.RuleNode(test_case)

    def test_parses_correctly(self):
        """
        Tests that parsing doesn't throw when given correct rules
        """
        test_cases = [
            ['ec2_instance', '(', 'tag:stack.state', '=', '"live"', ')', '{', '}']
        ]

        for test_case in test_cases:
            try:
                nodes.RuleNode(test_case)
            except errors.ParsingError:
                self.fail('Error parsing valid rule')

class ResourceNodeTests(unittest.TestCase):
    """
    Tests for the ResourceNode which determines the resource
    that a rule operates over
    """
    def test_accepts_valid_resources(self):
        """
        Tests that ResourceNode's can be constructed
        based on all the valid resource types we look at
        """
        valid_resources = ['ec2_instance']
        for resource in valid_resources:
            node = nodes.ResourceNode([resource])
            self.assertEqual(node.get_resource_name(), resource)

    def test_rejects_invalid_resources(self):
        """
        Tests that attempting to construct a resource node
        from an invalid resource name fails
        """
        invalid_resources = ['a_random_resource', 'resource2']
        for resource in invalid_resources:
            with self.assertRaises(errors.ParsingError):
                nodes.ResourceNode([resource])
