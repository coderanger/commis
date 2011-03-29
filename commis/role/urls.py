from django.conf.urls.defaults import url, patterns

from commis.role.views import role

urlpatterns = patterns('',
    url(r'^/(?P<name>[^/]*)', role, name='role_get'),
    url(r'', role, name='role_list'),
)
