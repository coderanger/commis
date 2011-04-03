import inspect
import re

ROUTE_PART = re.compile(r'\{(?P<name>\w+)\}')

def route_from_string(s):
    converted = ROUTE_PART.sub(r'(?P<\1>[^/]+)', s)
    if converted:
        converted = '^/' + converted
    return converted

def route_from_function(fn):
    argspec = inspect.getargspec(fn)
    route = '/'.join('{%s}'%arg for arg in argspec.args if arg != 'self' and arg != 'request')
    return route_from_string(route)
