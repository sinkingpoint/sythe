class MissingArgumentError(Exception):
    """
    Raised when an expected argument for an action
    is not provided
    """
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message

class InvalidArgumentError(Exception):
    """
    Raised when the value to an argument given to an action
    is invalid in the context of the action
    """
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message
