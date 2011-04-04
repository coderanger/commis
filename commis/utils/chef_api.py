import base64
import datetime
import itertools
import traceback

from chef.auth import sha1_base64, canonical_request
from chef.rsa import SSLError
from django.http import HttpResponse

from commis import conf
from commis.exceptions import ChefAPIError
from commis.clients.models import Client
from commis.utils import json

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
    qs = Client.objects.filter(name=user_id.strip())
    if not qs:
        raise ChefAPIError(401, 'Failed to authenticate. Ensure that your client key is valid')
    return qs[0]


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


def decode_json(request):
    request.json = None
    if request.META.get('CONTENT_TYPE') == 'application/json' and request.raw_post_data:
        try:
            request.json = json.loads(request.raw_post_data)
        except ValueError:
            pass


def create_error(msg, code):
    return HttpResponse(json.dumps({'error': msg, 'traceback': traceback.format_exc()}), status=code, content_type='application/json')


def verify_request(request):
    hashed_body = hash_body(request)
    timestamp = decode_timestamp(request)
    client = decode_client(request)
    verify_timestamp(request, timestamp)
    verify_signature(request, timestamp, client, hashed_body)
    verify_body_hash(request, hashed_body)
    return client


def execute_request(view, request, *args, **kwargs):
    if view is None:
        return create_error('No method found', 404)
    try:
        client = verify_request(request)
        decode_json(request)
        request.client = client
        data = view(request, *args, **kwargs)
        if not isinstance(data, HttpResponse):
            data = HttpResponse(json.dumps(data), content_type='application/json')
        return data
    except ChefAPIError, e:
        return create_error(e.msg, e.code)
    except Exception, e:
        return create_error(str(e), 500)
