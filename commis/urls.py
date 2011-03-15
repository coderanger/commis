from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^api/', include('commis.api.urls')),
    url(r'', include('commis.webui.urls')),
)
