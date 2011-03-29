from django.conf.urls.defaults import url, patterns

from commis.cookbook.views import cookbook

urlpatterns = patterns('',
    url(r'^/(?P<name>[^/]*)/(?P<version>[^/]*)/files/(?P<checksum>[^/]*)', cookbook, name='cookbook_file'),
    url(r'^/(?P<name>[^/]*)/(?P<version>[^/]*)', cookbook, name='cookbook_version'),
    url(r'^/(?P<name>[^/]*)', cookbook, name='cookbook_get'),
    url(r'', cookbook, name='cookbook_list'),
)
