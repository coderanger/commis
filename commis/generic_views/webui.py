from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import classonlymethod
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _

from commis.generic_views.base import CommisGenericViewBase
from commis.webui.utils import get_deleted_objects

class CommisView(CommisGenericViewBase):
    form = None
    search_key = 'name'

    def get_create_form(self, request):
        if hasattr(self, 'create_form'):
            return self.create_form
        return self.form

    def get_edit_form(self, request):
        if hasattr(self, 'edit_form'):
            return self.edit_form
        return self.form

    def get_object(self, request, name):
        return get_object_or_404(self.model, **{self.search_key: name})

    def index(self, request):
        opts = self.model._meta
        return TemplateResponse(request, ('commis/%s/index.html'%self.get_app_label(), 'commis/generic/index.html'), {
            'opts': opts,
            'object_list': self.model.objects.all(),
            'action': 'list',
            'block_title': opts.verbose_name_plural.capitalize(),
            'block_nav': self.block_nav(),
            'show_view': 'commis_webui_%s_show'%self.get_app_label(),
            'edit_view': 'commis_webui_%s_edit'%self.get_app_label(),
            'delete_view': 'commis_webui_%s_delete'%self.get_app_label(),
        })

    def create(self, request):
        opts = self.model._meta
        form_class = self.get_create_form(request)
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Created %s %s'%(opts.verbose_name, form.cleaned_data[self.search_key]))
                return HttpResponseRedirect(reverse('commis_webui_%s_index'%self.get_app_label()))
        else:
            form = form_class()
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': self.model(),
            'form': form,
            'action': 'create',
            'block_title': opts.verbose_name.capitalize(),
            'block_nav': self.block_nav(),
        })

    def show(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        return TemplateResponse(request, ('commis/%s/show.html'%self.get_app_label(), 'commis/generic/show.html'), {
            'opts': opts,
            'obj': obj,
            'action': 'show',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(obj),
        })

    def edit(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        form_class = self.get_edit_form(request)
        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edited %s %s'%(opts.verbose_name, form.cleaned_data[self.search_key]))
                return HttpResponseRedirect(reverse('commis_webui_%s_index'%self.get_app_label()))
        else:
            form = form_class(instance=obj)
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': obj,
            'form': form,
            'action': 'edit',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(obj),
        })

    def delete(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        deleted_objects, perms_needed, protected = get_deleted_objects(obj, request)
        if request.POST: # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj.delete()
            messages.success(request, _(u'Deleted %s %s')%(opts.verbose_name, obj))
            return HttpResponseRedirect(reverse('commis_webui_%s_index'%self.get_app_label()))
        return TemplateResponse(request, ('commis/%s/delete.html'%self.get_app_label(), 'commis/generic/delete.html'), {
            'opts': opts,
            'obj': obj,
            'action': 'delete',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(obj),
            'deleted_objects': deleted_objects,
            'perms_lacking': perms_needed,
            'protected': protected,
        })

    def block_nav(self, obj=None):
        data = {
            'index': reverse('commis_webui_%s_index'%self.get_app_label()),
            'create': reverse('commis_webui_%s_create'%self.get_app_label()),
        }
        if obj is not None:
            data.update({
                'show': reverse('commis_webui_%s_show'%self.get_app_label(), args=(obj,)),
                'edit': reverse('commis_webui_%s_edit'%self.get_app_label(), args=(obj,)),
                'delete': reverse('commis_webui_%s_delete'%self.get_app_label(), args=(obj,)),
            })
        return data

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return view(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.index),
                name='commis_webui_%s_index' % self.get_app_label()),
            url(r'^new/$',
                wrap(self.create),
                name='commis_webui_%s_create' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/delete/$',
                wrap(self.delete),
                name='commis_webui_%s_delete' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/edit/$',
                wrap(self.edit),
                name='commis_webui_%s_edit' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/$',
                wrap(self.show),
                name='commis_webui_%s_show' % self.get_app_label()),
        )
        return urlpatterns
