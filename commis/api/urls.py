from django.conf.urls.defaults import url, patterns

from commis.api import views

urlpatterns = patterns('',
    url('^(?:/(?P<name>.*))?', views.client, name='client'),
)
