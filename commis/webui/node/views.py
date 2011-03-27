from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from commis.api.node.models import Node
from commis.webui.node.forms import NodeForm

from django.utils.decorators import classonlymethod
from django.utils.functional import update_wrapper

class CommisGenericView(object):
    model = None
    form = None

    def index(self, request):
        opts = self.model._meta
        return TemplateResponse(request, ('commis/%s/index.html'%opts.app_label, 'commis/generic/index.html'), {
            'opts': opts,
            'object_list': self.model.objects.all(),
            'action': 'list',
            'block_nav': self.block_nav(),
            'show_view': 'commis_webui_%s_show'%opts.app_label,
            'edit_view': 'commis_webui_%s_edit'%opts.app_label,
            'delete_view': 'commis_webui_%s_delete'%opts.app_label,
        })

    def create(self, request):
        opts = self.model._meta
        if request.method == 'POST':
            form = self.form(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Created %s %s'%(opts.verbose_name, form.cleaned_data['name']))
                return HttpResponseRedirect(reverse('commis_webui_%s_index'%opts.app_label))
        else:
            form = self.form()
        return TemplateResponse(request, ('commis/%s/edit.html'%opts.app_label, 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': self.model(),
            'form': form,
            'action': 'create',
            'block_nav': self.block_nav(),
        })

    def show(self, request, name):
        opts = self.mode._meta
        obj = get_object_or_404(self.model, name=name)
        return TemplateResponse(request, ('commis/%s/show.html'%opts.app_label, 'commis/generic/show.html'), {
            'opts': opts,
            'obj': obj,
            'action': 'show',
            'block_nav': self.block_nav(obj),
        })

    def edit(self, request, name):
        opts = self.model._meta
        obj = get_object_or_404(self.model, name=name)
        if request.method == 'POST':
            form = NodeForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edited %s %s'%(opts.verbose_name, form.cleaned_data['name']))
                return HttpResponseRedirect(reverse('commis_webui_%s_index'%opts.app_label))
        else:
            form = NodeForm(instance=obj)
        return TemplateResponse(request, ('commis/%s/edit.html'%opts.app_label, 'commis/generic/edit.html'), {
            'opts': opts,
            'obj': obj,
            'form': form,
            'action': 'edit',
            'block_nav': self.block_nav(obj),
        })

    def delete(self, request, name):
        pass

    def block_nav(self, obj=None):
        opts = self.model._meta
        data = {
            'index': reverse('commis_webui_%s_index'%opts.app_label),
            'create': reverse('commis_webui_%s_create'%opts.app_label),
        }
        if obj is not None:
            data.update({
                'show': reverse('commis_webui_%s_show'%opts.app_label, args=(obj,)),
                'edit': reverse('commis_webui_%s_edit'%opts.app_label, args=(obj,)),
                'delete': reverse('commis_webui_%s_delete'%opts.app_label, args=(obj,)),
            })
        return data

    @property
    def urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return view(*args, **kwargs)
            return update_wrapper(wrapper, view)

        app_label = self.model._meta.app_label

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.index),
                name='commis_webui_%s_index' % app_label),
            url(r'^new/$',
                wrap(self.create),
                name='commis_webui_%s_create' % app_label),
            url(r'^(?P<name>[^/]+)/delete/$',
                wrap(self.delete),
                name='commis_webui_%s_delete' % app_label),
            url(r'^(?P<name>[^/]+)/edit/$',
                wrap(self.edit),
                name='commis_webui_%s_edit' % app_label),
            url(r'^(?P<name>[^/]+)/$',
                wrap(self.show),
                name='commis_webui_%s_show' % app_label),
        )
        return urlpatterns

    @classonlymethod
    def as_view(cls):
        self = cls()
        return self.urls


class NodeView(CommisGenericView):
    model = Node
    form = NodeForm


def index(request):
    return TemplateResponse(request, 'commis/node/index.html', {
        'opts': Node._meta,
        'object_list': Node.objects.all(),
        'action': 'list',
    })


def create(request):
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Created node %s'%form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('commis-webui-node-index'))
    else:
        form = NodeForm()
    return TemplateResponse(request, 'commis/node/edit.html', {
        'opts': Node._meta,
        'obj': Node(),
        'form': form,
        'action': 'create',
    })


def show(request, name):
    pass


def edit(request, name):
    node = get_object_or_404(Node, name=name)
    if request.method == 'POST':
        form = NodeForm(request.POST, instance=node)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited node %s'%form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('commis-webui-node-index'))
    else:
        form = NodeForm(instance=node)
    return TemplateResponse(request, 'commis/node/edit.html', {
        'opts': Node._meta,
        'obj': node,
        'form': form,
        'action': 'edit',
    })


def delete(request, name):
    pass
