from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView

from commis.clients.views import ClientAPIView, ClientView
from commis.cookbooks.views import CookbookAPIView, CookbookView
from commis.data_bags.views import DataBagAPIView, DataBagView
from commis.nodes.views import NodeAPIView, NodeView
from commis.roles.views import RoleAPIView, RoleView
from commis.sandboxes.views import SandboxAPIView
from commis.search.views import SearchAPIView, SearchView
from commis.status.views import StatusView
from commis.users.views import UserView
from commis.environments.views import EnvironmentAPIView


urlpatterns = patterns('',
    url(r'^api/clients', include(ClientAPIView.as_view())),
    url(r'^api//?cookbooks', include(CookbookAPIView.as_view())),
    url(r'^api/data', include(DataBagAPIView.as_view())),
    url(r'^api/nodes', include(NodeAPIView.as_view())),
    url(r'^api/roles', include(RoleAPIView.as_view())),
    url(r'^api/sandboxes', include(SandboxAPIView.as_view())),
    url(r'^api/search', include(SearchAPIView.as_view())),
    url(r'^api/environments', include(EnvironmentAPIView.as_view())),

    url(r'^clients/', include(ClientView.as_view())),
    url(r'^cookbooks/', include(CookbookView.as_view())),
    url(r'^databags/', include(DataBagView.as_view())),
    url(r'^nodes/', include(NodeView.as_view())),
    url(r'^roles/', include(RoleView.as_view())),
    url(r'^search/', include(SearchView.as_view())),
    url(r'^status/', include(StatusView.as_view())),
    url(r'^users/', include(UserView.as_view())),
    url(r'^$', TemplateView.as_view(template_name='commis/index.html'), name='commis_webui'),
)
