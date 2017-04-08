from sythe.errors import RegistryCollisionError
class Registry:
    """
    A class which provides a registration service.
    Classes can call `register` as a decorator to register
    themselves with a name
    """
    def __init__(self):
        self.registered = {}

    def register(self, name):
        """Used as a decorator, to register a class under a given name"""
        def register_class(klass):
            if name in self.registered:
                raise RegistryCollisionError('Name {} already in Registry'.format(name))
            self.registered[name] = klass
            return klass
        return register_class

    def __contains__(self, key):
        return key in self.registered

    def __getitem__(self, key):
        return self.registered[key]

resource_registry = Registry()
operator_registry = Registry()
