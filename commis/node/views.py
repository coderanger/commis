from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api.decorators import chef_api
from commis.exceptions import ChefAPIError
from commis.cookbook.models import Cookbook
from commis.node.forms import NodeForm
from commis.node.models import Node
from commis.utils import json
from commis.webui.views import CommisGenericView

@chef_api()
def node_list(request):
    data = {}
    for node in Node.objects.all():
        data[node.name] = request.build_absolute_uri(reverse('node_get', args=[node.name]))
    return data

@chef_api()
def node_create(request):
    if not request.client.admin and not request.client.validator:
        raise ChefAPIError(401, 'You are not allowed to take this action')
    if Node.objects.filter(name=request.json['name']).exists():
        raise ChefAPIError(409, 'Node %s already exists', request.json['name'])
    node = Node.objects.from_dict(request.json)
    data = {'uri': request.build_absolute_uri(reverse('node_get', args=[node.name]))}
    return HttpResponse(json.dumps(data), status=201)


@chef_api()
def node_get(request, name):
    try:
        node = Node.objects.get(name=name)
    except Node.DoesNotExist:
        raise ChefAPIError(404, 'Node %s not found', name)
    return node


@chef_api()
def node_update(request, name):
    if not request.client.admin and not request.client.name == name:
        raise ChefAPIError(401, 'You are not allowed to take this action')
    if request.json['name'] != name:
        raise ChefAPIError(500, 'Name mismatch')
    if not Node.objects.filter(name=name).exists():
        raise ChefAPIError(404, 'Node %s not found', name)
    return Node.objects.from_dict(request.json)


@chef_api()
def node_delete(request, name):
    if not request.client.admin and not request.client.name == name:
        raise ChefAPIError(401, 'You are not allowed to take this action')
    try:
        node = Node.objects.get(name=name)
    except Node.DoesNotExist:
        raise ChefAPIError(404, 'Node %s not found', request.json['name'])
    node.delete()
    return node

@chef_api()
def node_cookbooks(request, name):
    if not request.client.admin and not request.client.name == name:
        raise ChefAPIError(401, 'You are not allowed to take this action')
    try:
        node = Node.objects.get(name=name)
    except Node.DoesNotExist:
        raise ChefAPIError(404, 'Node %s not found', request.json['name'])
    candidates = set([recipe.split('::', 1)[0] for recipe in node.expand_run_list()])
    cookbooks = {}
    while candidates:
        candidate = candidates.pop()
        if candidate in cookbooks:
            continue # Already checked
        qs = Cookbook.objects.filter(name=candidate).order_by('version')
        if not qs:
            continue # Error?
        candidate_cookbook = qs[0]
        for dep in candidate_cookbook.dependencies.all():
            candidates.add(dep.name)
        cookbooks[candidate] = candidate_cookbook.to_dict(request)
    return cookbooks


@csrf_exempt
def node(request, name=None, cookbooks=False):
    if not name:
        if request.method == 'GET':
            return node_list(request)
        if request.method == 'POST':
            return node_create(request)
    else:
        if request.method == 'GET':
            if cookbooks:
                return node_cookbooks(request, name)
            else:
                return node_get(request, name)
        if request.method == 'PUT':
            return node_update(request, name)
        if request.method == 'DELETE':
            return node_delete(request, name)
    raise Http404


class NodeView(CommisGenericView):
    model = Node
    form = NodeForm
