from django.conf.urls.defaults import patterns, url

from commis.webui.user import views

urlpatterns = patterns('',
    url(r'^new/', views.create, name='commis-webui-user-create'),
    url(r'^(?P<username>[^/]+)/delete/', views.delete, name='commis-webui-user-delete'),
    url(r'^(?P<username>[^/]+)/edit/', views.edit, name='commis-webui-user-edit'),
    url(r'^(?P<username>[^/]+)/', views.show, name='commis-webui-user-show'),
    url(r'^$', views.index, name='commis-webui-user-index'),
)
