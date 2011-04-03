from django.conf.urls.defaults import patterns, url, include

from commis.cookbook.views import CookbookAPIView
from commis.data_bag.views import DataBagAPIView
from commis.node.views import NodeAPIView
from commis.role.views import RoleAPIView
from commis.search.views import SearchAPIView

urlpatterns = patterns('',
    url(r'^api/cookbooks', include(CookbookAPIView.as_view())),
    url(r'^api/data', include(DataBagAPIView.as_view())),
    url(r'^api/nodes', include(NodeAPIView.as_view())),
    url(r'^api/roles', include(RoleAPIView.as_view())),
    url(r'^api/search', include(SearchAPIView.as_view())),
    url(r'', include('commis.webui.urls')),
)
