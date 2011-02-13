from django.conf.urls.defaults import url, patterns

from commis.api import views

urlpatterns = patterns('',
    url('^/?', views.list, name='client-list'),
)
