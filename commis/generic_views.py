from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator, classonlymethod

from commis.api.decorators import verify_request, decode_json, create_error
from commis.exceptions import ChefAPIError
from commis.utils import json

def api(url, method, admin=False):
    def dec(fn):
        fn._commis_api = {
            'name': fn.__name__,
            'url': url,
            'method': method,
            'admin': admin,
        }
        return fn
    return dec


class _DispatchView(object):
    def __init__(self, view_map):
        self.view_map = view_map
        if 'GET' in view_map:
            name = view_map['GET'].__name__
        else:
            name = view_map.values()[0].__name__
        self.name = 'commis_api_role_'+name

    def __call__(self, instance):
        return _BoundDispatchView(self, instance)


class _BoundDispatchView(object):
    def __init__(self, dispatch_view, instance):
        self.dispatch_view = dispatch_view
        self.instance = instance

    def __call__(self, request, *args, **kwargs):
        view = self.dispatch_view.view_map.get(request.method)
        if view is None:
            return create_error('No method found', 404)
        try:
            client = verify_request(request)
            if view._commis_api['admin'] and not client.admin:
                raise ChefAPIError(403, 'You are not allowed to take this action')
            decode_json(request)
            request.client = client
            data = view(self.instance, request, *args, **kwargs)
            if not isinstance(data, HttpResponse):
                data = HttpResponse(json.dumps(data), content_type='application/json')
            return data
        except ChefAPIError, e:
            return create_error(e.msg, e.code)
        except Exception, e:
            import traceback; traceback.print_exc()
            return create_error(str(e), 500)


class CommisAPIGenericViewMeta(type):
    def __init__(self, name, bases, d):
        self.views = {}
        for name, obj in d.iteritems():
            if hasattr(obj, '_commis_api'):
                #view = method_decorator(chef_api(admin=obj._commis_api['admin']))(obj)
                #view._commis_api = obj._commis_api
                self.views.setdefault(obj._commis_api['url'], {})[obj._commis_api['method']] = getattr(self, name)

        self.dispatch_views = {}
        for url_pattern, view_map in self.views.iteritems():
            self.dispatch_views[url_pattern] = _DispatchView(view_map)


class CommisGenericViewBase(object):
    model = None

    @property
    def urls(self):
        return self.get_urls()

    @classonlymethod
    def as_view(cls):
        self = cls()
        return self.urls


class CommisAPIGenericView(object):
    __metaclass__ = CommisAPIGenericViewMeta
    model = None

    def get_urls(self):
        urlpatterns = patterns('')
        for url_pattern, dispatch_view in sorted(self.dispatch_views.iteritems(), reverse=True):
            urlpatterns.append(url(url_pattern, dispatch_view(self), name=dispatch_view.name))
        return urlpatterns
