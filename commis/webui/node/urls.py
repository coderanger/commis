from django.conf.urls.defaults import patterns, url

from commis.webui.node import views

urlpatterns = patterns('',
    url(r'^new/$', views.create, name='commis-webui-node-create'),
    url(r'^(?P<name>[^/]+)/delete/$', views.delete, name='commis-webui-node-delete'),
    url(r'^(?P<name>[^/]+)/edit/$', views.edit, name='commis-webui-node-edit'),
    url(r'^(?P<name>[^/]+)/$', views.show, name='commis-webui-node-show'),
    url(r'^$', views.index, name='commis-webui-node-index'),
)
