import unittest
from sythe.registry import Registry
from sythe.errors import RegistryCollisionError

class RegistryTests(unittest.TestCase):
    def test_registry_registers(self):
        registry = Registry()
        @registry.register('A')
        class AClass:
            pass

        self.assertEqual(registry['A'], AClass)

    def test_registry_throws_on_double_register(self):
        registry = Registry()
        @registry.register('A')
        class AClass:
            pass

        with self.assertRaises(RegistryCollisionError):
            @registry.register('A')
            class BClass:
                pass
