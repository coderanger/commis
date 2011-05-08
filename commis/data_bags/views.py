import functools

from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _

from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api, CommisView
from commis.data_bags.forms import DataBagForm, DataBagItemForm
from commis.data_bags.models import DataBag, DataBagItem
from commis.db import update

class DataBagAPIView(CommisAPIView):
    model = DataBag
    item_model = DataBagItem

    def get_item_or_404(self, bag_name, name):
        bag = self.get_or_404(bag_name)
        try:
            return bag.items.get(name=name)
        except self.item_model.DoesNotExist:
            raise ChefAPIError(404, '%s %s::%s not found', self.item_model._meta.verbose_name.capitalize(), bag_name, name)

    def get_data(self, request, bag):
        data = {}
        for item in bag.items.all():
            data[item.name] = self.reverse(request, 'item_get', bag, item)
        return data

    @api('POST', admin=True)
    def item_create(self, request, name):
        if not request.json or 'id' not in request.json:
            raise ChefAPIError(500, 'No item ID specified')
        bag = self.get_or_404(name)
        if bag.items.filter(name=request.json['id']).exists():
            raise ChefAPIError(409, 'Data bag item %s::%s already exists', name, request.json['id'])
        bag.items.create(name=request.json['id'], data=request.raw_post_data)
        return request.json

    @api('GET')
    def item_get(self, request, bag_name, name):
        item = self.get_item_or_404(bag_name, name)
        return HttpResponse(item.data, status=200, content_type='application/json')

    @api('PUT', admin=True)
    def item_update(self, request, bag_name, name):
        if not request.json:
            raise ChefAPIError(500, 'No data sent')
        if request.json.get('id') != name:
            raise ChefAPIError(500, 'Name mismatch in data bag item')
        item = self.get_item_or_404(bag_name, name)
        update(item, data=request.raw_post_data)
        return HttpResponse(item.data, status=200, content_type='application/json')

    @api('DELETE', admin=True)
    def item_delete(self, request, bag_name, name):
        item = self.get_item_or_404(bag_name, name)
        item.delete()
        return HttpResponse(item.data, status=200, content_type='application/json')


class DataBagView(CommisView):
    model = DataBag
    item_model = DataBagItem
    form = DataBagForm
    item_form = DataBagItemForm

    def show_response(self, request, obj):
        response = super(DataBagView, self).list_response(request, obj.items.all())
        response.context_data['obj'] = obj
        response.context_data['action'] = 'show'
        response.context_data['block_nav'] = self.block_nav(request, obj)
        return response

    def create_item(self, request, name):
        opts = self.item_model._meta
        bag = self.get_object(request, name)
        self.assert_permission(request, 'create_item', bag)
        form_class = functools.partial(self.item_form, bag)
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Created %(verbose_name)s %(object)s')%{'verbose_name':opts.verbose_name, 'object':form.cleaned_data[self.search_key]})
                return self.change_redirect(request, 'create_item', form.instance)
        else:
            form = form_class()
        response = self.create_response(request, form)
        response.context_data['action'] = 'create_item'
        response.context_data['block_nav'] = self.block_nav(request, bag)
        return response

    def show_item(self, request, name, item_name):
        bag = self.get_object(request, name)
        try:
            item = bag.items.get(name=item_name)
        except self.item_model.DoesNotExist:
            raise Http404
        return super(DataBagView, self).show_response(request, item)

    def reverse(self, request, action, *args):
        if args and isinstance(args[0], self.item_model):
            action += '_item'
            args = args[0].bag.name, args[0].name
        return super(DataBagView, self).reverse(request, action, *args)

    def block_nav(self, request, obj=None):
        data = super(DataBagView, self).block_nav(request, obj)
        if obj is not None:
            if isinstance(obj, self.model):
                if self.has_permission(request, 'create_item', obj):
                    data.insert(data.keyOrder.index('show'), 'create_item', {'label': _('Create Item'), 'link': self.reverse(request, 'create_item', obj)})
            elif isinstance(obj, self.item_model):
                pass
        return data

    def change_redirect(self, request, action, obj):
        if action.endswith('_item'):
            if self.has_permission(request, 'show_item', obj):
                return HttpResponseRedirect(reverse('commis_webui_%s_show_item'%self.get_app_label(), args=(obj.bag, obj)))
            elif self.has_permission(request, 'show', obj.bag):
                return HttpResponseRedirect(reverse('commis_webui_%s_show'%self.get_app_label(), args=(obj.bag,)))
            else:
                return HttpResponseRedirect(reverse('commis_webui_%s_list'%self.get_app_label()))
        return super(DataBagView, self).change_redirect(request, action, obj)

    # XXX: With a better permissions system this shouldn't be needed at all. <NPK 2011-05-07>
    def has_permission(self, request, action, obj=None):
        if action.endswith('_item'):
            action = {
                'create_item': 'edit',
                'show_item': 'show',
                'edit_item': 'edit',
                'delete_item': 'delete',
            }[action]
        return super(DataBagView, self).has_permission(request, action, obj)

    def get_urls(self):
        return super(DataBagView, self).get_urls() + patterns('',
            url(r'^(?P<name>[^/]+)/new/$',
                self.create_item,
                name='commis_webui_%s_create_item' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/(?P<item_name>[^/]+)/delete/$',
                self.show_item,
                name='commis_webui_%s_delete_item' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/(?P<item_name>[^/]+)/edit/$',
                self.show_item,
                name='commis_webui_%s_edit_item' % self.get_app_label()),
            url(r'^(?P<name>[^/]+)/(?P<item_name>[^/]+)/$',
                self.show_item,
                name='commis_webui_%s_show_item' % self.get_app_label()),
        )