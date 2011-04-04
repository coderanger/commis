from django.conf.urls.defaults import patterns, url, include

from commis.clients.views import ClientAPIView
from commis.cookbooks.views import CookbookAPIView
from commis.data_bags.views import DataBagAPIView
from commis.nodes.views import NodeAPIView
from commis.roles.views import RoleAPIView
from commis.sandboxes.views import SandboxAPIView
from commis.search.views import SearchAPIView

urlpatterns = patterns('',
    url(r'^api/clients', include(ClientAPIView.as_view())),
    url(r'^api/cookbooks', include(CookbookAPIView.as_view())),
    url(r'^api/data', include(DataBagAPIView.as_view())),
    url(r'^api/nodes', include(NodeAPIView.as_view())),
    url(r'^api/roles', include(RoleAPIView.as_view())),
    url(r'^api/sandboxes', include(SandboxAPIView.as_view())),
    url(r'^api/search', include(SearchAPIView.as_view())),
    url(r'', include('commis.webui.urls')),
)
