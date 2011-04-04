from django.conf.urls.defaults import url, patterns

from commis.data_bag.views import data_bag

urlpatterns = patterns('',
    url(r'^/(?P<bag_name>[^/]+)/(?P<name>.+)', data_bag, name='data_bag_item_get'),
    url(r'^/(?P<name>[^/]+)', data_bag, name='data_bag_get'),
    url(r'', data_bag, name='data_bag_list'),
)
