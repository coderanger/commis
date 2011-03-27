from django.conf.urls.defaults import patterns, url, include

from commis.webui import views

urlpatterns = patterns('',
    url(r'^users/', include('commis.webui.user.urls')),
    url(r'^nodes/', include('commis.webui.node.urls')),
    url(r'^$', views.index, name='commis-webui-index'),
)