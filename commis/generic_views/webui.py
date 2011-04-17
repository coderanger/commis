from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

from commis.exceptions import InsuffcientPermissions
from commis.generic_views.base import CommisGenericViewBase
from commis.utils.deleted_objects import get_deleted_objects

class CommisViewBase(CommisGenericViewBase):
    form = None
    create_form = None
    edit_form = None
    search_key = 'name'

    def get_create_form(self, request):
        if self.create_form is not None:
            return self.create_form
        return self.form

    def get_edit_form(self, request):
        if self.edit_form is not None:
            return self.edit_form
        return self.form

    def get_object(self, request, name):
        return get_object_or_404(self.model, **{self.search_key: name})

    def has_permission(self, request, action, obj=None):
        if action == 'list' or action == 'show':
            # I don't, yet, have an actual Django permission for list or show
            return request.user.is_authenticated()
        # Django spells these actions differently
        django_action = {
            'create': 'add',
            'edit': 'change',
            'delete': 'delete',
        }[action]
        return request.user.has_perm('%s.%s_%s'%(self.get_app_label(), django_action, self.get_model_name().lower()), obj)

    def block_nav(self, request, obj=None):
        data = {
            'name': self.model and self.model.__name__.lower() or self.get_app_label(),
            'list': reverse('commis_webui_%s_list'%self.get_app_label()),
        }
        if self.has_permission(request, 'create'):
            data['create'] = reverse('commis_webui_%s_create'%self.get_app_label())
        if obj is not None:
            if self.has_permission(request, 'show', obj):
                data['show'] = reverse('commis_webui_%s_show'%self.get_app_label(), args=(obj,))
            if self.has_permission(request, 'edit', obj):
                data['edit'] = reverse('commis_webui_%s_edit'%self.get_app_label(), args=(obj,))
            if self.has_permission(request, 'delete', obj):
                data['delete'] = reverse('commis_webui_%s_delete'%self.get_app_label(), args=(obj,))
        return data


class CommisView(CommisViewBase):
    def list(self, request):
        opts = self.model._meta
        if not self.has_permission(request, 'list'):
            raise InsuffcientPermissions(self.model, 'list')
        return TemplateResponse(request, ('commis/%s/list.html'%self.get_app_label(), 'commis/generic/list.html'), {
            'opts': opts,
            'object_list': [(obj, self.block_nav(request, obj)) for obj in self.model.objects.all()],
            'action': 'list',
            'block_title': opts.verbose_name_plural.capitalize(),
            'block_nav': self.block_nav(request),
        })

    def create(self, request):
        opts = self.model._meta
        if not self.has_permission(request, 'create'):
            raise InsuffcientPermissions(self.model, 'create')
        form_class = self.get_create_form(request)
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Created %(verbose_name)s %(object)s')%{'verbose_name':opts.verbose_name, 'object':form.cleaned_data[self.search_key]})
                return self.change_redirect(request, 'create', form.instance)
        else:
            form = form_class()
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': self.model(),
            'form': form,
            'action': 'create',
            'block_title': opts.verbose_name.capitalize(),
            'block_nav': self.block_nav(request),
        })

    def show(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        if not self.has_permission(request, 'show', obj):
            raise InsuffcientPermissions(self.model, 'show')
        return TemplateResponse(request, ('commis/%s/show.html'%self.get_app_label(), 'commis/generic/show.html'), {
            'opts': opts,
            'obj': obj,
            'action': 'show',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(request, obj),
        })

    def edit(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        if not self.has_permission(request, 'edit', obj):
            raise InsuffcientPermissions(self.model, 'edit')
        form_class = self.get_edit_form(request)
        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, _('Edited %(verbose_name)s %(object)s')%{'verbose_name':opts.verbose_name, 'object':form.cleaned_data[self.search_key]})
                return self.change_redirect(request, 'edit', obj)
        else:
            form = form_class(instance=obj)
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': obj,
            'form': form,
            'action': 'edit',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(request, obj),
        })

    def delete(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        if not self.has_permission(request, 'delete', obj):
            raise InsuffcientPermissions(self.model, 'delete')
        deleted_objects, perms_needed, protected = get_deleted_objects(obj, request)
        if request.POST: # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj.delete()
            messages.success(request, _(u'Deleted %s %s')%(opts.verbose_name, obj))
            return self.change_redirect(request, 'delete', obj)
        return TemplateResponse(request, ('commis/%s/delete.html'%self.get_app_label(), 'commis/generic/delete.html'), {
            'opts': opts,
            'obj': obj,
            'action': 'delete',
            'block_title': u'%s %s'%(opts.verbose_name.capitalize(), obj),
            'block_nav': self.block_nav(request, obj),
            'deleted_objects': deleted_objects,
            'perms_lacking': perms_needed,
            'protected': protected,
        })

    def change_redirect(self, request, action, obj):
        if self.has_permission(request, 'show', obj):
            return HttpResponseRedirect(reverse('commis_webui_%s_show'%self.get_app_label(), args=(obj,)))
        else:
            return HttpResponseRedirect(reverse('commis_webui_%s_list'%self.get_app_label()))

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$',
                self.list,
                name='commis_webui_%s_list' % self.get_app_label()),
            url(r'^new/$',
                self.create,
                name='commis_webui_%s_create' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/delete/$',
                self.delete,
                name='commis_webui_%s_delete' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/edit/$',
                self.edit,
                name='commis_webui_%s_edit' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/$',
                self.show,
                name='commis_webui_%s_show' % self.get_app_label()),
        )
        return urlpatterns
