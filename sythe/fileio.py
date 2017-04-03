"""
This module provides IO operations for moving rules between text
representations and internal AST representations
"""

import sythe.parsing.strings as strings

def parse_rules_from_file(file_path):
    """
    This function reads the given file and parses
    all the rule definitions, throwing a ParsingError
    if they are incorrect
    """
    with open(file_path, 'r') as rule_file:
        raw_file_contents = rule_file.read()

    return strings.parse_rules_from_string(raw_file_contents)
