from django.conf.urls.defaults import patterns, url, include

from commis.webui import views
from commis.webui.node.views import NodeView

urlpatterns = patterns('',
    url(r'^users/', include('commis.webui.user.urls')),
    url(r'^nodes/', include(NodeView.as_view())),
    url(r'^$', views.index, name='commis-webui-index'),
)
