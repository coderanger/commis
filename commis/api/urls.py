from django.conf.urls.defaults import url, patterns, include

from commis.api.views import client
from commis.api.sandbox.views import sandbox
from commis.api.cookbook.views import cookbook

urlpatterns = patterns('',
    url(r'^clients(?:/(?P<name>.*))?', client, name='client'),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)/(?P<checksum>[^/]*)', sandbox),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)', sandbox),
    url(r'^sandboxes', sandbox),
    url(r'^cookbooks/(?P<name>[^/]*)/(?P<version>[^/]*)/files/(?P<checksum>[^/]*)', cookbook),
    url(r'^cookbooks/(?P<name>[^/]*)/(?P<version>[^/]*)', cookbook),
    url(r'^cookbooks/(?P<name>[^/]*)', cookbook),
    url(r'^cookbooks', cookbook),
    url(r'^nodes', include('commis.api.node.urls')),
    url(r'^roles', include('commis.api.role.urls')),
)
