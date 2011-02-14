from commis.api.decorators import chef_api
from commis.api.models import Client

@chef_api()
def list(request):
    data = {}
    for client in Client.objects.all():
        data[client.name] = request.build_absolute_uri('/clients/'+client.name)
    return data
