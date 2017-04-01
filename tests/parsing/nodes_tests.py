import unittest
import sythe.parsing.nodes as nodes
import sythe.parsing.errors as errors

class IsolateConditionTests(unittest.TestCase):
    """
    Tests the isolate_condition function which scans
    tokens to find the contents of the condition for a rule
    """
    def test_handles_unstarted(self):
        """
        Tests that an error is thrown when
        the given tokens don't start at a condition
        """
        test_cases = [
            ['A'],
            ['{', 'B', '=', 'C', '}']
        ]

        for test_case in test_cases:
            with self.assertRaises(errors.ParsingError):
                nodes.isolate_condition(test_case)

    def test_handles_unmatched(self):
        """
        Tests that an error is thrown when we're given
        unproperly terminated conditions
        """
        test_cases = [
            ['('],
            ['(', 'B', '=', '(', ')'],
            ['(', 'B', '=', '(', 'A', '>', 'C']
        ]

        for test_case in test_cases:
            with self.assertRaises(errors.ParsingError):
                nodes.isolate_condition(test_case)

    def test_isolates_correctly(self):
        """
        Tests that we can find the correct span of a condition
        """
        test_cases = [
            (['(', 'A', '=', 'B', ')'], 5),
            (['(', '(', 'A', '=', 'B', ')', '&', 'C', ')'], 9),
            (['(', 'A', '=', 'B', ')', 'C', 'X'], 5)
        ]

        for test_case, expected_output in test_cases:
            output = nodes.isolate_condition(test_case)
            self.assertEqual(output, expected_output)

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

class ConditionalNodeTests(unittest.TestCase):
    """
    Tests for the ConditionNode which is basically the rule engine
    part of the parser
    """
    def test_rejects_invalid_operations(self):
        """
        This test makes sure that parsing fails on invalid operations
        """
        test_cases = ['m', '[', ',', '/']
        for test_case in test_cases:
            condition = ['(', 'A', test_case, 'B', ')']
            with self.assertRaises(errors.ParsingError):
                nodes.parse_condition(condition)

    def test_rejects_unclosed_strings(self):
        """
        This test makes sure that improperly closed strings
        are not parsed
        """
        test_cases = [
            '\'asdf',
            '\"asdf',
            'asdf\'',
            'asdf\"',
            '\'asdf\"',
            '\"asdf\''
        ]

        for test_case in test_cases:
            condition = ['(', test_case, '>', 'B', ')']
            with self.assertRaises(errors.ParsingError):
                nodes.parse_condition(condition)

    def test_parses_correctly(self):
        """
        This test makes sure that no errors are thrown on valid conditions
        """
        test_cases = [
            ['(', 'A', '=', 'B', ')'],
            ['(', 'A', '>', 'B', '&', 'AB', '>', 'BA', ')'],
            ['(', '(', 'A', '>', 'B', '|', 'AB', '>', 'BA', ')', '&', 'ABC', '=', 'CBA', ')']
        ]

        for test_case in test_cases:
            test_case_str = ' '.join(test_case)
            try:
                nodes.parse_condition(test_case)
            except errors.ParsingError as err:
                self.fail('Expected {} to parse correctly. Got: {}'.format(test_case_str, err.message))

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
