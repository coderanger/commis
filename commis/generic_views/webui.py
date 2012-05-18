from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.datastructures import SortedDict
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
        permission = '%s.%s_%s'%(self.get_app_label(), django_action, self.get_model_name().lower())
        return request.user.has_perm(permission)

    def assert_permission(self, request, action, obj=None):
        if not self.has_permission(request, action, obj):
            raise InsuffcientPermissions(self.model, action)

    def reverse(self, request, action, *args):
        return reverse('commis_webui_%s_%s'%(self.get_app_label(), action), args=args)

    def block_nav(self, request, obj=None):
        data = SortedDict()
        data.name = self.model and self.model.__name__.lower() or self.get_app_label()
        data['list'] = {'label': _('List'), 'link': self.reverse(request, 'list')}
        if self.has_permission(request, 'create'):
            data['create'] = {'label': _('Create'), 'link': self.reverse(request, 'create')}
        if obj is not None:
            if self.has_permission(request, 'show', obj):
                data['show'] = {'label': _('Show'), 'link': self.reverse(request, 'show', obj)}
            if self.has_permission(request, 'edit', obj):
                data['edit'] = {'label': _('Edit'), 'link': self.reverse(request, 'edit', obj)}
            if self.has_permission(request, 'delete', obj):
                data['delete'] = {'label': _('Delete'), 'link': self.reverse(request, 'delete', obj)}
        return data


class CommisView(CommisViewBase):
    def list(self, request):
        self.assert_permission(request, 'list')
        return self.list_response(request, self.model.objects.all())

    def list_response(self, request, qs):
        opts = self.model._meta
        return TemplateResponse(request, ('commis/%s/list.html'%self.get_app_label(), 'commis/generic/list.html'), {
            'opts': opts,
            'object_list': [(obj, self.block_nav(request, obj)) for obj in qs],
            'action': 'list',
            'block_nav': self.block_nav(request),
        })

    def create(self, request):
        opts = self.model._meta
        self.assert_permission(request, 'create')
        form_class = self.get_create_form(request)
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Created %(verbose_name)s %(object)s')%{'verbose_name':opts.verbose_name, 'object':form.cleaned_data[self.search_key]})
                return self.change_redirect(request, 'create', form.instance)
        else:
            form = form_class()
        return self.create_response(request, form)

    def create_response(self, request, form):
        opts = self.model._meta
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': self.model(),
            'form': form,
            'action': 'create',
            'block_nav': self.block_nav(request),
        })

    def show(self, request, name):
        obj = self.get_object(request, name)
        self.assert_permission(request, 'show', obj)
        return self.show_response(request, obj)

    def show_response(self, request, obj):
        opts = self.model._meta
        return TemplateResponse(request, 'commis/%s/show.html'%self.get_app_label(), {
            'opts': opts,
            'obj': obj,
            'action': 'show',
            'block_nav': self.block_nav(request, obj),
        })

    def edit(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        self.assert_permission(request, 'edit', obj)
        form_class = self.get_edit_form(request)
        if request.method == 'POST':
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, _('Edited %(verbose_name)s %(object)s')%{'verbose_name':opts.verbose_name, 'object':form.cleaned_data[self.search_key]})
                return self.change_redirect(request, 'edit', obj)
        else:
            form = form_class(instance=obj)
        return self.edit_response(request, obj, form)

    def edit_response(self, request, obj, form):
        opts = self.model._meta
        return TemplateResponse(request, ('commis/%s/edit.html'%self.get_app_label(), 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': obj,
            'form': form,
            'action': 'edit',
            'block_nav': self.block_nav(request, obj),
        })

    def delete(self, request, name):
        opts = self.model._meta
        obj = self.get_object(request, name)
        self.assert_permission(request, 'delete', obj)
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
            'block_nav': self.block_nav(request, obj),
            'deleted_objects': deleted_objects,
            'perms_lacking': perms_needed,
            'protected': protected,
        })

    def change_redirect(self, request, action, obj):
        if action != 'delete' and self.has_permission(request, 'show', obj):
            name, args = 'show', (obj,)
        else:
            name, args = 'list', ()
        url = reverse('commis_webui_%s_%s' % (self.get_app_label(), name), args=args)
        return HttpResponseRedirect(url)

    def get_urls(self):
        return patterns('',
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
