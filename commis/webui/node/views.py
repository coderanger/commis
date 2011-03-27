from commis.api.node.models import Node
from commis.webui.views import CommisGenericView
from commis.webui.node.forms import NodeForm

class NodeView(CommisGenericView):
    model = Node
    form = NodeForm
