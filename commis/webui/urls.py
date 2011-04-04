from django.conf.urls.defaults import patterns, url, include

from commis.webui import views
from commis.nodes.views import NodeView
from commis.webui.user.views import UserView

urlpatterns = patterns('',
    url(r'^users/', include(UserView.as_view())),
    url(r'^nodes/', include(NodeView.as_view())),
    url(r'^$', views.index, name='commis-webui-index'),
)
