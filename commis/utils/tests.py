from django.utils import unittest

from commis.utils.dict import deep_merge, flatten_dict
from commis.utils.routes import route_from_string, route_from_function

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


class RoutesTestCase(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(route_from_string(''), '')
        self.assertEqual(route_from_string('{foo}'), '^/(?P<foo>[^/]+)')
        self.assertEqual(route_from_string('{foo}/{bar}'), '^/(?P<foo>[^/]+)/(?P<bar>[^/]+)')

    def test_from_function(self):
        self.assertEqual(route_from_function(lambda: None), '')
        self.assertEqual(route_from_function(lambda self: None), '')
        self.assertEqual(route_from_function(lambda self, request: None), '')
        self.assertEqual(route_from_function(lambda foo: None), '^/(?P<foo>[^/]+)')
        self.assertEqual(route_from_function(lambda request, foo: None), '^/(?P<foo>[^/]+)')
        self.assertEqual(route_from_function(lambda self, request, foo: None), '^/(?P<foo>[^/]+)')
        self.assertEqual(route_from_function(lambda foo, bar: None), '^/(?P<foo>[^/]+)/(?P<bar>[^/]+)')
        self.assertEqual(route_from_function(lambda request, foo, bar: None), '^/(?P<foo>[^/]+)/(?P<bar>[^/]+)')
        self.assertEqual(route_from_function(lambda self, request, foo, bar: None), '^/(?P<foo>[^/]+)/(?P<bar>[^/]+)')
