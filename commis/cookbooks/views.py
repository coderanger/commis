from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.template.response import TemplateResponse
from pkg_resources import parse_version

from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api, CommisViewBase
from commis.cookbooks.models import Cookbook, CookbookFile

class CookbookAPIView(CommisAPIView):
    model = Cookbook

    @api('GET')
    def get(self, request, name):
        versions = Cookbook.objects.filter(name=name).values_list('version', flat=True)
        if not versions:
            raise ChefAPIError(404, 'Cookbook %s not found', name)
        return {name: versions}

    @api('GET')
    def version(self, request, name, version):
        try:
            cookbook = Cookbook.objects.get(name=name, version=version)
        except Cookbook.DoesNotExist:
            raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
        return cookbook.to_dict(request)

    @api('PUT', admin=True)
    def update(self, request, name, version):
        cookbook = Cookbook.objects.from_dict(request.json)
        return cookbook.to_dict(request)

    @api('DELETE', admin=True)
    def delete(self, request, name, version):
        qs = Cookbook.objects.filter(name=name, version=version)
        if not qs.exists():
            raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
        qs.delete()
        return {}

    @api('GET', '{name}/{version}/files/{checksum}')
    def file(self, request, name, version, checksum):
        qs = CookbookFile.objects.select_related('file').filter(cookbook__name=name, cookbook__version=version, file__checksum=checksum, file__uploaded=True)
        if not qs:
            raise ChefAPIError(404, 'File not found')
        cookbook_file = qs[0]
        response = HttpResponse(open(cookbook_file.file.path, 'rb').read(), content_type=cookbook_file.file.content_type)
        return response


class CookbookView(CommisViewBase):
    model = Cookbook

    def has_permission(self, request, action, obj=None):
        if action != 'list' and action != 'show':
            return False
        return super(CookbookView, self).has_permission(request, action, obj)

    def list(self, request, name=None):
        opts = self.model._meta
        self.assert_permission(request, 'list')
        qs = self.model.objects.all()
        if name:
            qs = qs.filter(name=name)
        cookbooks = {}
        for obj in qs:
            cookbooks.setdefault(obj.name, []).append((obj, self.block_nav(obj)))
        for name, cookbook_list in cookbooks.iteritems():
            cookbook_list.sort(key=lambda x: parse_version(x[0].version), reverse=True)
        cookbooks = sorted(cookbooks.iteritems())
        return TemplateResponse(request, 'commis/%s/list.html'%self.get_app_label(), {
            'opts': opts,
            'object_list': cookbooks,
            'action': 'list',
            'block_title': opts.verbose_name_plural.capitalize(),
            'block_nav': self.block_nav(request),
        })

    def show(self, request, name, version):
        opts = self.model._meta
        obj = self.get_object(request, name)
        self.assert_permission(request, 'show', obj)
        return TemplateResponse(request, 'commis/%s/show.html'%self.get_app_label(), {
            'opts': opts,
            'obj': obj,
            'action': 'show',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(request, obj),
        })

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$',
                self.list,
                name='commis_webui_%s_list' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/$',
                self.list,
                name='commis_webui_%s_list_single' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/(?P<version>[^/]+)/$',
                self.show,
                name='commis_webui_%s_show' % self.get_app_label()),
        )
        return urlpatterns
