from django.utils import unittest

from commis.utils.dict import deep_merge, flatten_dict

class DictTestCase(unittest.TestCase):
    def test_deep_merge(self):
        a = {
            'a': 1,
            'b': 2,
            'c': {
                'd': 3,
                'e': 4,
            }
        }
        b = {
            'a': 10,
            'd': 3,
            'c': {
                'd': 10,
                'f': 4,
            }
        }
        data = deep_merge(a, b)
        self.assertEqual(data, {
            'a': 1,
            'b': 2,
            'd': 3,
            'c': {
                'd': 3,
                'e': 4,
                'f': 4,
            }
        })

    def test_flatten_dict(self):
        data = {
            'a': 1,
            'b': 2,
            'c': {
                'b': 3,
                'd': 4,
            }
        }
        self.assertEqual(flatten_dict(data), {
            'a': [1],
            'b': [3, 2],
            'd': [4],
            'c_b': [3],
            'c_d': [4],
        })