from commis.cookbook.models import Cookbook
from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api, CommisView
from commis.node.forms import NodeForm
from commis.node.models import Node

class NodeAPIView(CommisAPIView):
    model = Node

    @api('POST')
    def create(self, request):
        if not request.client.admin and not request.client.validator:
            raise ChefAPIError(401, 'You are not allowed to take this action')
        return super(NodeAPIView, self).create(request)

    @api('PUT')
    def update(self, request, name):
        if not request.client.admin and not request.client.name == name:
            raise ChefAPIError(401, 'You are not allowed to take this action')
        return super(NodeAPIView, self).update(request, name)

    @api('DELETE')
    def node_delete(self, request, name):
        if not request.client.admin and not request.client.name == name:
            raise ChefAPIError(401, 'You are not allowed to take this action')
        return super(NodeAPIView, self).delete(request, name)

    @api('GET', '{name}/cookbooks')
    def node_cookbooks(self, request, name):
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


class NodeView(CommisView):
    model = Node
    form = NodeForm
