import base64
import datetime
import functools
import itertools
import json

from chef.auth import sha1_base64, canonical_request
from chef.rsa import SSLError
from django.conf import settings
from django.http import HttpResponse

from commis.api import conf
from commis.api.exceptions import ChefAPIError
from commis.api.models import Client

def decode_timestamp(request):
    timestamp = request.META.get('HTTP_X_OPS_TIMESTAMP')
    if not timestamp:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')
    return datetime.datetime.strptime(timestamp.strip(), '%Y-%m-%dT%H:%M:%SZ')


def hash_body(request):
    return sha1_base64(request.raw_post_data)


def decode_client(request):
    user_id = request.META.get('HTTP_X_OPS_USERID')
    if not user_id:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')
    return Client.objects.get(name=user_id.strip())


def decode_signature(request):
    request_signature = []
    for i in itertools.count(1):
        hdr = request.META.get('HTTP_X_OPS_AUTHORIZATION_%s'%i)
        if not hdr:
            break
        request_signature.append(hdr.strip())
    return base64.b64decode(''.join(request_signature))


def verify_timestamp(request, timestamp):
    delta = datetime.datetime.utcnow() - timestamp
    if abs(delta.total_seconds()) > conf.COMMIS_TIME_SKEW:
        raise ChefAPIError(401, 'Failed to authenticate. Please synchronize the clock on your client')


def verify_signature(request, timestamp, client, hashed_body):
    candidate_block = canonical_request(request.method, request.path, hashed_body, timestamp, client.name)
    request_signature = decode_signature(request)
    if not request_signature:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')
    try:
        decrypted_block = client.key.public_decrypt(request_signature)
    except SSLError:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')
    if candidate_block != decrypted_block:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')


def verify_body_hash(request, hashed_body):
    candidate_hash = request.META.get('HTTP_X_OPS_CONTENT_HASH', '').strip()
    if candidate_hash != hashed_body:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')


def chef_api(admin=False, admin_or_validator=False, admin_or_node=False):
    def dec(fn):
        @functools.wraps(fn)
        def wrapper(request, *args, **kwargs):
            try:
                hashed_body = hash_body(request)
                timestamp = decode_timestamp(request)
                client = decode_client(request)
                verify_timestamp(request, timestamp)
                verify_signature(request, timestamp, client, hashed_body)
                verify_body_hash(request, hashed_body)
                if admin and not client.admin:
                    raise ChefAPIError(403, 'You are not allowed to take this action')
                data = fn(request, *args, **kwargs)
                return HttpResponse(json.dumps(data))
            except ChefAPIError, e:
                return HttpResponse(json.dumps({'error': e.msg}), status=e.code)
            except Exception, e:
                return HttpResponse(json.dumps({'error': str(e)}), status=500)
        return wrapper
    return dec
