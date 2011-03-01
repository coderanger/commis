from django.conf.urls.defaults import url, patterns

from commis.api.search.views import search

urlpatterns = patterns('',
    url(r'^/(?P<name>[^/]+)', search, name='search_get'),
    url(r'', search, name='search_list'),
)
