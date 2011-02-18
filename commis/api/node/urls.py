from django.conf.urls.defaults import url, patterns

from commis.api.node.views import node

urlpatterns = patterns('',
    url(r'^/(?P<name>[^/]*)/cookbooks', node, name='node_cookbooks', kwargs={'cookbooks': True}),
    url(r'^/(?P<name>[^/]*)', node, name='node_get'),
    url(r'', node, name='node_list'),
)
