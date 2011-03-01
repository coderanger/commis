import hashlib

import chef
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api import conf
from commis.api.decorators import chef_api
from commis.api.exceptions import ChefAPIError
from commis.api.cookbook.models import Cookbook
from commis.api.data_bag.models import DataBag, DataBagItem
from commis.db import update
from commis.utils import json

@chef_api()
def data_bag_list(request):
    data = {}
    for bag in DataBag.objects.all():
        data[bag.name] = request.build_absolute_uri(reverse('data_bag_get', args=[bag.name]))
    return data


@chef_api(admin=True)
def data_bag_create(request):
    if DataBag.objects.filter(name=request.json['name']).exists():
        raise ChefAPIError(409, 'Data bag %s already exists', request.json['name'])
    bag = DataBag.objects.create(name=request.json['name'])
    data = {'uri': request.build_absolute_uri(reverse('data_bag_get', args=[bag.name]))}
    return HttpResponse(json.dumps(data), status=201, content_type='application/json')


@chef_api()
def data_bag_get(request, name):
    try:
        bag = DataBag.objects.get(name=name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', name)
    data = {}
    for item in bag.items.all():
        data[item.name] = request.build_absolute_uri(reverse('data_bag_item_get', args=[name, item.name]))
    return data


@chef_api(admin=True)
def data_bag_delete(request, name):
    try:
        bag = DataBag.objects.get(name=name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', name)
    bag.delete()
    return {}


@chef_api(admin=True)
def data_bag_item_create(request, name):
    if not request.json or 'id' not in request.json:
        raise ChefAPIError(500, 'No item ID specified')
    try:
        bag = DataBag.objects.get(name=name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', name)
    if bag.items.filter(name=request.json['id']).exists():
        raise ChefAPIError(409, 'Data bag item %s::%s already exists', name, request.json['id'])
    bag.items.create(name=request.json['id'], data=request.raw_post_data)
    return request.json


@chef_api()
def data_bag_item_get(request, bag_name, name):
    try:
        bag = DataBag.objects.get(name=bag_name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', bag_name)
    try:
        item = bag.items.get(name=name)
    except DataBagItem.DoesNotExist:
        raise ChefAPIError(404, 'Data bag item %s::%s not found', bag_name, name)
    return HttpResponse(item.data, status=200, content_type='application/json')


@chef_api(admin=True)
def data_bag_item_update(request, bag_name, name):
    if not request.json:
        raise ChefAPIError(500, 'No data sent')
    if request.json.get('id') != name:
        raise ChefAPIError(500, 'Name mismatch in data bag item')
    try:
        bag = DataBag.objects.get(name=bag_name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', bag_name)
    try:
        item = bag.items.get(name=name)
    except DataBagItem.DoesNotExist:
        raise ChefAPIError(404, 'Data bag item %s::%s not found', bag_name, name)
    update(item, data=request.raw_post_data)
    return HttpResponse(item.data, status=200, content_type='application/json')


@chef_api(admin=True)
def data_bag_item_delete(request, bag_name, name):
    try:
        bag = DataBag.objects.get(name=bag_name)
    except DataBag.DoesNotExist:
        raise ChefAPIError(404, 'Data bag %s not found', bag_name)
    try:
        item = bag.items.get(name=name)
    except DataBagItem.DoesNotExist:
        raise ChefAPIError(404, 'Data bag item %s::%s not found', bag_name, name)
    item.delete()
    return HttpResponse(item.data, status=200, content_type='application/json')


@csrf_exempt
def data_bag(request, bag_name=None, name=None):
    if not bag_name and not name:
        if request.method == 'GET':
            return data_bag_list(request)
        if request.method == 'POST':
            return data_bag_create(request)
    elif not bag_name:
        if request.method == 'GET':
            return data_bag_get(request, name)
        if request.method == 'POST':
            return data_bag_item_create(request, name)
        if request.method == 'DELETE':
            return data_bag_delete(request, name)
    else:
        if request.method == 'GET':
            return data_bag_item_get(request, bag_name, name)
        if request.method == 'PUT':
            return data_bag_item_update(request, bag_name, name)
        if request.method == 'DELETE':
            return data_bag_item_delete(request, bag_name, name)
    raise Http404
