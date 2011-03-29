from django.conf.urls.defaults import url, patterns, include

from commis.api.views import client

urlpatterns = patterns('',
    url(r'^clients(?:/(?P<name>.*))?', client, name='client'),
    url(r'^sandboxes', include('commis.sandbox.urls')),
    url(r'^cookbooks', include('commis.cookbook.urls')),
    url(r'^nodes', include('commis.node.urls')),
    url(r'^roles', include('commis.role.urls')),
    url(r'^search', include('commis.search.urls')),
    url(r'^data', include('commis.data_bag.urls')),
    url(r'^search', include('commis.search.urls')),
)
