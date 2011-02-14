import chef
from django.http import Http404

from commis.api import conf
from commis.api.decorators import chef_api
from commis.api.models import Client

@chef_api()
def client_list(request):
    data = {}
    for client in Client.objects.all():
        data[client.name] = request.build_absolute_uri('/clients/'+client.name)
    return data

@chef_api()
def client_create(request):
    if not (client.admin or client.name == conf.COMMIS_VALIDATOR_NAME):
        raise ChefAPIError(403, 'You are not allowed to take this action')

@chef_api()
def client_get(request, name):
    return Client.objects.get(name=name)

@chef_api(admin=True)
def client_update(request, name):
    pass

@chef_api(admin=True)
def client_delete(request, name):
    pass

def client(request, name=None):
    if request.method == 'GET':
        if name:
            return client_get(request, name)
        return client_list(request)
    if request.method == 'POST' and not name:
        return client_create(request)
    if request.method == 'PUT' and name:
        return client_update(request, name)
    if request.method == 'DELETE' and name:
        return client_delete(request, name)
    raise Http404
