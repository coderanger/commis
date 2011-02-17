from django.conf.urls.defaults import url, patterns

from commis.api.views import client
from commis.api.sandbox.views import sandbox

urlpatterns = patterns('',
    url(r'^clients(?:/(?P<name>.*))?', client, name='client'),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)/(?P<checksum>[^/]*)', sandbox),
    url(r'^sandboxes/(?P<sandbox_id>[^/]*)', sandbox),
    url(r'^sandboxes', sandbox),
)
