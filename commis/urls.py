from django.conf.urls.defaults import patterns, url, include

from commis.node.views import NodeAPIView
from commis.role.views import RoleAPIView

urlpatterns = patterns('',
    url(r'^api/nodes', include(NodeAPIView.as_view())),
    url(r'^api/roles', include(RoleAPIView.as_view())),
    url(r'', include('commis.webui.urls')),
)
