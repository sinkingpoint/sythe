import unittest
from sythe.parsing import tokenizer

class TokenizerTests(unittest.TestCase):
    def test_tokenizer_tests(self):
        """
        Tests that the string tokenizer tokenizes strings
        as we expect before parsing
        """
        test_cases = [
            #Test Empty strings don't have any tokens
            ('', []),

            #Check identifiers work
            ('ec2_instance', ['ec2_instance']),

            #Check empty conditions still get parenthesis
            ('ec2_instance()', ['ec2_instance', '(', ')']),

            #Check basic arguments are split
            ('ec2_instance(state="up")', ['ec2_instance', '(', 'state', '=', '"up"', ')']),

            #Check whitespace is ignored in arguments
            ('ec2_instance(state = "up")', ['ec2_instance', '(', 'state', '=', '"up"', ')']),

            #Check logical operations are split correctly
            ('ec2_instance(state="up"&tag:stack.state="superceded")',
             ['ec2_instance', '(', 'state', '=', '"up"', '&',
              'tag:stack.state', '=', '"superceded"', ')']),

            ('ec2_instance(state="up"|tag:stack.state="superceded")',
             ['ec2_instance', '(', 'state', '=', '"up"', '|',
              'tag:stack.state', '=', '"superceded"', ')']),

            #Check empty blocks are split correctly
            ('ec2_instance(state="up"|tag:stack.state="superceded") {}',
             ['ec2_instance', '(', 'state', '=', '"up"', '|',
              'tag:stack.state', '=', '"superceded"', ')', '{', '}']),

            ('ec2_instance(state="up"|tag:stack.state="superceded"){add_tag "a", "b"}',
             ['ec2_instance', '(', 'state', '=', '"up"', '|',
              'tag:stack.state', '=', '"superceded"', ')', '{', 'add_tag',
              '"a"', ',', '"b"', '}'])
        ]

        for test_input, output in test_cases:
            tokenized = tokenizer.tokenize_string(test_input)
            self.assertEqual(tokenized, output)
