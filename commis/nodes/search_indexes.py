from haystack import site

from commis.nodes.models import Node
from commis.search.indexes import CommisSearchIndex

class NodeIndex(CommisSearchIndex):
    pass

site.register(Node, NodeIndex)
