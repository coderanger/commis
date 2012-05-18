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
        return super(ClientAPIView, self).create(request)

    def create_data(self, request, obj):
        data = super(ClientAPIView, self).create_data(request, obj)
        # Initial creation (via ClientManager.from_dict, which should end up
        # being called by our parent classes) attaches a temporary .private_key
        # attribute which we can send back to the Chef client.
        data['private_key'] = obj.private_key
        return data


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
