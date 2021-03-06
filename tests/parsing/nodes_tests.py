import unittest
from unittest.mock import MagicMock
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
            ['ec2_instance', '(', 'tag:stack.state', '=', '"live"', ')', '{', '}'],
            ['ec2_instance', '(', 'tag:stack.state', '=', '"live"', ')', '{',
             'mark_for_deletion', '(', 'after:', '"3 days"', ')',
             '}'],
            ['ec2_instance', '(', 'tag:stack.state', '=', '"live"', ')', '{',
             'email', '(', 'to:', 'tag:owner', ',', 'from:', "someone", ')',
             '}']
        ]

        for test_case in test_cases:
            test_case_str = ' '.join(test_case)
            try:
                nodes.RuleNode(test_case)
            except errors.ParsingError:
                self.fail('Error parsing valid rule: {}'.format(test_case_str))

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
            self.assertEqual(node.resource_name, resource)

    def test_rejects_invalid_resources(self):
        """
        Tests that attempting to construct a resource node
        from an invalid resource name fails
        """
        invalid_resources = ['a_random_resource', 'resource2']
        for resource in invalid_resources:
            with self.assertRaises(errors.ParsingError):
                nodes.ResourceNode([resource])

class ActionNodeTests(unittest.TestCase):
    def test_invalid_actions_fail(self):
        test_cases = [
            ['test', 'vimda'], #( must be after action name
            ['test', '('], #parameter list must be terminated
            ['test', '(', ',', ')'], #misplaced comma
            ['test', '(', ':%&^%:', '"vimda"', ')'], #invalid parameter name
            ['test', '(', 'vomda:', '"vimda', ')'], #unterminated string
            ['test', '(', 'vomda:', '"vimda', ',', ')'] #superfluous comma
        ]

        for test_case in test_cases:
            with(self.assertRaises(errors.ParsingError)):
                nodes.ActionNode(test_case)

    def test_valid_actions_parse(self):
        test_cases = [
            (['test', '(', ')'], 'test', {}),
            (['test', '(', 'vimda:', '"vimda"', ')'], 'test', {'vimda': nodes.StringLiteralNode('"vimda"')}),
            (['test', '(', 'vimda:', '"vimda"', ',', 'vomda:', '"vomda"', ')'], 'test', {'vimda': nodes.StringLiteralNode('"vimda"'), 'vomda': nodes.StringLiteralNode('"vomda"')})
        ]

        for tokens, name, params in test_cases:
            node = nodes.ActionNode(tokens)
            self.assertEqual(node.action_name, name)
            self.assertEqual(node.arguments, params)

    def test_action_executes(self):
        resource = MagicMock()
        resource.action = MagicMock()
        node = nodes.ActionNode(['action', '(', 'vimda:', '"vimda"', ')'])
        node.execute(resource)
        resource.action.assert_called_once_with({'vimda': 'vimda'})

class AndNodeTests(unittest.TestCase):
    def test_and_ands(self):
        test_cases = [
            [nodes.BooleanLiteralNode(True), nodes.BooleanLiteralNode(True), True],
            [nodes.BooleanLiteralNode(True), nodes.BooleanLiteralNode(False), False],
            [nodes.BooleanLiteralNode(False), nodes.BooleanLiteralNode(True), False],
            [nodes.BooleanLiteralNode(False), nodes.BooleanLiteralNode(False), False]
        ]

        for left, right, output in test_cases:
            self.assertEqual(nodes.AndNode(left, right).execute(None), output)

class OrNodeTests(unittest.TestCase):
    def test_or_ors(self):
        test_cases = [
            (nodes.BooleanLiteralNode(True), nodes.BooleanLiteralNode(True), True),
            (nodes.BooleanLiteralNode(True), nodes.BooleanLiteralNode(False), True),
            (nodes.BooleanLiteralNode(False), nodes.BooleanLiteralNode(True), True),
            (nodes.BooleanLiteralNode(False), nodes.BooleanLiteralNode(False), False)
        ]

        for left, right, output in test_cases:
            self.assertEqual(nodes.OrNode(left, right).execute(None), output)

class EqualsNodeTests(unittest.TestCase):
    def test_equals_node_equals(self):
        test_cases = [
            (nodes.StringLiteralNode('"vimda"'), nodes.StringLiteralNode('"vimda"'), True),
            (nodes.StringLiteralNode('"vomda"'), nodes.StringLiteralNode('"vimda"'), False),
        ]

        for left, right, output in test_cases:
            self.assertEqual(nodes.EqualsNode(left, right).execute(None), output)

class VariableNodeTests(unittest.TestCase):
    def test_invalid_paths_returns_none(self):
        test_cases = [
            'some.none.existant.path',
            'some.broken.path.',
            'a.something'
        ]

        for path in test_cases:
            node = nodes.VariableNode(path)
            resource = {
                'a': {
                    'b': {}
                }
            }
            self.assertEqual(None, node.execute(resource))

    def test_correct_paths(self):
        test_cases = [
            'a',
            'b.c'
        ]

        for path in test_cases:
            node = nodes.VariableNode(path)
            resource = {
                'a': 3,
                'b': {
                    'c': 4
                }
            }
            node.execute(resource)

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
                nodes.parse_condition_to_ast(condition)

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
                nodes.parse_condition_to_ast(condition)

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
                nodes.parse_condition_to_ast(test_case)
            except errors.ParsingError as err:
                self.fail('Expected {} to parse correctly. Got: {}'.format(test_case_str, err.message))
