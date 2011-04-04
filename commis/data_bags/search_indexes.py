from haystack import indexes, site

from commis.data_bags.models import DataBagItem
from commis.search.indexes import CommisSearchIndex

class DataBagItemIndex(CommisSearchIndex):
    data_bag = indexes.CharField(model_attr='bag__name')

site.register(DataBagItem, DataBagItemIndex)
