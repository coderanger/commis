from django.template.response import TemplateResponse

from commis import conf
from commis.clients.forms import ClientForm, ClientEditForm
from commis.clients.models import Client
from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api, CommisView

class ClientAPIView(CommisAPIView):
    model = Client

    @api('POST')
    def create(self, request):
        if not (request.client.admin or request.client.name == conf.COMMIS_VALIDATOR_NAME):
            raise ChefAPIError(403, 'You are not allowed to take this action')
        super(ClientAPIView, self).create(request)


class ClientView(CommisView):
    model = Client
    form = ClientForm
    edit_form = ClientEditForm

    def change_redirect(self, request, action, obj):
        if not obj.key.public:
            # Rekey occured
            opts = self.model._meta
            return TemplateResponse(request, 'commis/%s/show.html'%self.get_app_label(), {
                'opts': opts,
                'obj': obj,
                'action': 'show',
                'block_nav': self.block_nav(request, obj),
            })
        return super(ClientView, self).change_redirect(request, action, obj)
