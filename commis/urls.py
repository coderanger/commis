from django.conf.urls.defaults import patterns, url, include

from commis.role.views import RoleAPIView

urlpatterns = patterns('',
    url(r'^api/roles', include(RoleAPIView.as_view())),
    url(r'', include('commis.webui.urls')),
)
