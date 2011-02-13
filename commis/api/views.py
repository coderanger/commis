import json

from django.http import HttpResponse

from commis.api.models import Client

def list(request):
    data = {}
    for client in Client.objects.all():
        data[client.name] = request.build_absolute_uri('/clients/'+client.name)
    return HttpResponse(json.dumps(data))
