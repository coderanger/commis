from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api.decorators import verify_request, decode_json, create_error
from commis.exceptions import ChefAPIError
from commis.generic_views.base import CommisGenericViewBase
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

    def __call__(self, instance):
        return _BoundDispatchView(self, instance)


class _BoundDispatchView(object):
    def __init__(self, dispatch_view, instance):
        csrf_exempt(self)
        self.dispatch_view = dispatch_view
        self.instance = instance
        if 'GET' in self.dispatch_view.view_map:
            name = self.dispatch_view.view_map['GET'].__name__
        else:
            name = self.dispatch_view.view_map.values()[0].__name__
        self.name = 'commis_api_%s_%s'%(instance.get_app_label(), name)

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


class CommisAPIViewMeta(type):
    def __init__(self, name, bases, d):
        super(CommisAPIViewMeta, self).__init__(name, bases, d)
        self.views = {}
        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_commis_api'):
                #view = method_decorator(chef_api(admin=obj._commis_api['admin']))(obj)
                #view._commis_api = obj._commis_api
                self.views.setdefault(obj._commis_api['url'], {})[obj._commis_api['method']] = getattr(self, name)

        self.dispatch_views = {}
        for url_pattern, view_map in self.views.iteritems():
            self.dispatch_views[url_pattern] = _DispatchView(view_map)


class CommisAPIView(CommisGenericViewBase):
    __metaclass__ = CommisAPIViewMeta
    model = None

    @api(r'', 'GET')
    def list(self, request):
        data = {}
        for obj in self.model.objects.all():
            data[obj.name] = request.build_absolute_uri(reverse('commis_api_%s_get'%self.get_app_label(), args=[obj.name]))
        return data

    def get_urls(self):
        urlpatterns = patterns('')
        for url_pattern, dispatch_view in sorted(self.dispatch_views.iteritems(), reverse=True):
            bound_view = dispatch_view(self)
            urlpatterns.append(url(url_pattern, bound_view, name=bound_view.name))
        return urlpatterns
