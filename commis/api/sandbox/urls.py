from django.conf.urls.defaults import url, patterns

from commis.api.sandbox.views import sandbox

urlpatterns = patterns('',
    url(r'^/(?P<sandbox_id>[^/]*)/(?P<checksum>[^/]*)', sandbox),
    url(r'^/(?P<sandbox_id>[^/]*)', sandbox),
    url(r'', sandbox),
)
