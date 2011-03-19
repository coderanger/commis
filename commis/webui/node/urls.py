from django.conf.urls.defaults import patterns, url

from commis.webui.node import views

urlpatterns = patterns('',
    url(r'', views.index, name='commis-webui-node-index'),
)
