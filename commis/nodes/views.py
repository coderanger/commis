from commis.cookbooks.models import Cookbook
from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api, CommisView
from commis.nodes.forms import NodeForm
from commis.nodes.models import Node


def authorize_client(self, request, name=None):
    # Normalize name -- in create hooks it comes from the form, not the URI
    # path
    node_name = name or request.json['name']
    if not request.client.admin and not request.client.name == node_name:
        raise ChefAPIError(401, 'You are not allowed to take this action')


class NodeAPIView(CommisAPIView):
    model = Node

    @api('POST', validator=authorize_client)
    def create(self, request):
        return super(NodeAPIView, self).create(request)

    @api('PUT', validator=authorize_client)
    def update(self, request, name):
        return super(NodeAPIView, self).update(request, name)

    @api('DELETE', validator=authorize_client)
    def node_delete(self, request, name):
        return super(NodeAPIView, self).delete(request, name)

    @api('GET', '{name}/cookbooks')
    def node_cookbooks(self, request, name):
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
