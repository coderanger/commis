from haystack import indexes, site

from commis.api.data_bag.models import DataBagItem
from commis.api.search.indexes import CommisSearchIndex

class DataBagItemIndex(CommisSearchIndex):
    data_bag = indexes.CharField(model_attr='bag__name')

site.register(DataBagItem, DataBagItemIndex)
