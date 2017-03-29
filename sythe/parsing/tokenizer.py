"""
This module handles logic for tokenizing rules scripts into
tokens, ready for parsing
"""

import regex

def tokenize_string(string):
    """
    Splits a given string into tokens, ready for parsing
    Arguments:
        string - The string to split
    Returns:
        A list of tokens from the string
    """
    #This regex splits on borders between tokens
    border_regex = r'\s+|(?=[()\[\]{};=&\|,])|(?<=[()\[\]{};=&\|,])'
    tokens = regex.split(border_regex, string, flags=regex.VERSION1)

    #Remove empty tokens
    tokens = [token for token in tokens if len(token) > 0]

    return tokens
