from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api.decorators import verify_request, decode_json, create_error
from commis.exceptions import ChefAPIError
from commis.generic_views.base import CommisGenericViewBase
from commis.utils import json, routes

def api(method, url=None, admin=False):
    def dec(fn):
        if url is not None:
            realurl = routes.route_from_string(url)
        else:
            realurl = routes.route_from_function(fn)
        fn._commis_api = {
            'name': fn.__name__,
            'url': realurl,
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


class CommisAPIViewBase(CommisGenericViewBase):
    __metaclass__ = CommisAPIViewMeta

    def reverse(self, request, tag, *args):
        return request.build_absolute_uri(reverse('commis_api_%s_%s'%(self.get_app_label(), tag), args=args))

    def get_urls(self):
        urlpatterns = patterns('')
        for url_pattern, dispatch_view in sorted(self.dispatch_views.iteritems(), reverse=True):
            bound_view = dispatch_view(self)
            urlpatterns.append(url(url_pattern, bound_view, name=bound_view.name))
        return urlpatterns


class CommisAPIView(CommisAPIViewBase):
    @api('GET')
    def list(self, request):
        data = {}
        # This could be sped up by using .values_list('name', flat=true)
        for obj in self.model.objects.all():
            data[obj.name] = self.reverse(request, 'get', obj)
        return data

    @api('POST', admin=True)
    def create(self, request):
        if self.model.objects.filter(name=request.json['name']).exists():
            raise ChefAPIError(409, '%s %s already exists', self.model._meta.verbose_name, request.json['name'])
        obj = self.model.objects.from_dict(request.json)
        data = self.create_data(request, obj)
        return HttpResponse(json.dumps(data), status=201, content_type='application/json')

    def create_data(self, request, obj):
        return {'uri': self.reverse(request, 'get', obj)}

    @api('GET')
    def get(self, request, name):
        try:
            obj = self.model.objects.get(name=name)
        except self.model.DoesNotExist:
            raise ChefAPIError(404, '%s %s not found', self.model._meta.verbose_name.capitalize(), name)
        return self.get_data(request, obj)

    def get_data(self, request, obj):
        return obj

    @api('PUT', admin=True)
    def update(self, request, name):
        if request.json['name'] != name:
            raise ChefAPIError(500, 'Name mismatch')
        if not self.model.objects.filter(name=name).exists():
            raise ChefAPIError(404, '%s %s not found', self.model._meta.verbose_name, name)
        obj = self.model.objects.from_dict(request.json)
        return self.update_data(request, obj)

    def update_data(self, request, obj):
        return obj

    @api('DELETE', admin=True)
    def delete(self, request, name):
        try:
            obj = self.model.objects.get(name=name)
        except self.model.DoesNotExist:
            raise ChefAPIError(404, '%s %s not found', self.model._meta.verbose_name, name)
        obj.delete()
        return self.delete_data(request, obj)

    def delete_data(self, request, obj):
        return obj
