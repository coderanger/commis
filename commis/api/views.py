import base64
import datetime
import itertools
import json

from django.http import HttpResponse
from chef.auth import sha1_base64, canonical_request
from chef.rsa import SSLError

from commis.api.models import Client

def list(request):
    hashed_body = sha1_base64(request.raw_post_data)
    timestamp = datetime.datetime.strptime(request.META['HTTP_X_OPS_TIMESTAMP'].strip(), '%Y-%m-%dT%H:%M:%SZ')
    user_id = request.META['HTTP_X_OPS_USERID'].strip()
    candidate = canonical_request(request.method, request.path, hashed_body, timestamp, user_id)
    client = Client.objects.get(name=user_id)
    request_signature = []
    for i in itertools.count(1):
        hdr = request.META.get('HTTP_X_OPS_AUTHORIZATION_%s'%i)
        if not hdr:
            break
        request_signature.append(hdr.strip())
    request_signature = base64.b64decode(''.join(request_signature))
    try:
        decrypt = client.key.public_decrypt(request_signature)
    except SSLError:
        return HttpResponse('{"error":"Failed the authorization check"}', status=401)
    if candidate != decrypt:
        return HttpResponse('{"error":"Failed the authorization check"}', status=401)

    data = {}
    for client in Client.objects.all():
        data[client.name] = request.build_absolute_uri('/clients/'+client.name)
    return HttpResponse(json.dumps(data))
