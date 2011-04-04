from haystack import site

from commis.node.models import Node
from commis.search.indexes import CommisSearchIndex

class NodeIndex(CommisSearchIndex):
    pass

site.register(Node, NodeIndex)
