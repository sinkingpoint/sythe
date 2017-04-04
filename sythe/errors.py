class MissingArgumentError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class InvalidArgumentError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

