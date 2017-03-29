import unittest
import sythe.parsing.nodes as nodes
import sythe.parsing.errors as errors

class ResourceNodeTests(unittest.TestCase):
    def test_resource_node_accepts_valid_resources(self):
        valid_resources = ['ec2_instance']
        for resource in valid_resources:
            node = nodes.ResourceNode([resource])
            self.assertEqual(node.get_resource_name(), resource)

    def test_resource_node_rejects_invalid_resources(self):
        invalid_resources = ['a_random_resource', 'resource2']
        for resource in invalid_resources:
            with self.assertRaises(errors.ParsingError):
                nodes.ResourceNode([resource])
