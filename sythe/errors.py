class MissingArgumentError(Exception):
    """
    Raised when an expected argument for an action
    is not provided
    """
    pass

class InvalidArgumentError(Exception):
    """
    Raised when the value to an argument given to an action
    is invalid in the context of the action
    """
    pass
