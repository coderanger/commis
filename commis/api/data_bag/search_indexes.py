from haystack import indexes, site

from commis.api.data_bag.models import DataBagItem
from commis.utils.dict import flatten_dict

class DataBagItemIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    data_bag = indexes.CharField(model_attr='bag__name')
    id_order = indexes.CharField()

    def prepare_text(self, item):
        buf = []
        for key, values in flatten_dict(item.to_search()).iteritems():
            for value in values:
                buf.append('%s__=__%s'%(key, value))
        return '\n'.join(buf)


        def prepare_id_order(self, item):
            return '%016d'%item.id


site.register(DataBagItem, DataBagItemIndex)
