from django.conf.urls.defaults import url, patterns

from commis.api.views import client
from commis.api.sandbox.views import sandbox

urlpatterns = patterns('',
    url('^clients(?:/(?P<name>.*))?', client, name='client'),
    url('^sandboxes(?:/(?P<sandbox_id>[^/]*(?:/(?P<checksum>.*))?))?', sandbox, name='sandbox'),
)
