from django.conf.urls.defaults import url, patterns, include

from commis.api.views import client
from commis.api.sandbox.views import sandbox

urlpatterns = patterns('',
    url(r'^clients(?:/(?P<name>.*))?', client, name='client'),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)/(?P<checksum>[^/]*)', sandbox),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)', sandbox),
    url(r'^sandboxes', sandbox),
    url(r'^cookbooks', include('commis.api.cookbook.urls')),
    url(r'^nodes', include('commis.api.node.urls')),
    url(r'^roles', include('commis.api.role.urls')),
    url(r'^search', include('commis.api.search.urls')),
    url(r'^data', include('commis.api.data_bag.urls')),
    url(r'^searcg', include('commis.api.search.urls')),
)
