from __future__ import absolute_import
import types
try: #pragma: no cover
    import json
except ImportError: #pragma: no cover
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.contrib.auth.models import User

def maybe_call(x):
    if callable(x):
        return x()
    return x

def user_to_dict(user):
    return {}

class JSONEncoder(DjangoJSONEncoder):
    """Custom encoder to allow arbitrary model classes."""

    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return maybe_call(obj.to_dict)
        elif hasattr(obj, 'to_list'):
            return maybe_call(obj.to_list)
        elif isinstance(obj, User):
            return user_to_dict(obj)
        elif isinstance(obj, QuerySet):
            return list(obj)
        elif isinstance(obj, types.GeneratorType):
            return list(obj)
        return super(JSONEncoder, self).default(obj)

load = json.load
loads = json.loads
dump = lambda obj: json.dump(obj, cls=JSONEncoder)
dumps = lambda obj: json.dumps(obj, cls=JSONEncoder)
