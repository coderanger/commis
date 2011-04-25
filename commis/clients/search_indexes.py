from haystack import site

from commis.clients.models import Client
from commis.search.indexes import CommisSearchIndex

class ClientIndex(CommisSearchIndex):
    pass

site.register(Client, ClientIndex)
