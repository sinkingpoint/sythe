"""
This module contains errors which can be raised during the parsing process
"""
class ParsingError(Exception):
    """
    A generic error raised when an assumption is broken
    when parsing a rule
    """
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message
