from haystack import indexes, site

from commis.api.data_bag.models import DataBagItem
from commis.utils.dict import flatten_dict

class DataBagItemIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    data_bag = indexes.CharField(model_attr='bag__name')

    def prepare_text(self, item):
        buf = []
        for key, values in flatten_dict(item.to_search()).iteritems():
            for value in values:
                buf.append('%s__=__%s'%(key, value))
        return '\n'.join(buf)


site.register(DataBagItem, DataBagItemIndex)
