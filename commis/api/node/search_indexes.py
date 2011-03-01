import collections

from haystack import indexes, site

from commis.api.node.models import Node
from commis.api.search.indexes import CommisSearchIndex

class NodeIndex(CommisSearchIndex):
    pass

site.register(Node, NodeIndex)
