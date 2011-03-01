import collections

from haystack import indexes, site

from commis.api.node.models import Node
from commis.utils.dict import flatten_dict

class NodeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    id_order = indexes.CharField()

    def prepare_text(self, node):
        buf = []
        for key, values in flatten_dict(node.to_search()).iteritems():
            for value in values:
                buf.append('%s__=__%s'%(key, value))
        return '\n'.join(buf)

    def prepare_id_order(self, node):
        return '%016d'%node.id


site.register(Node, NodeIndex)
