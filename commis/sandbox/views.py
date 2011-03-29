import hashlib

from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from commis.api.decorators import chef_api
from commis.exceptions import ChefAPIError
from commis.sandbox.models import Sandbox, SandboxFile
from commis.db import update

@chef_api(admin=True)
def sandbox_create(request):
    checksums = request.json['checksums'].keys()
    sandbox = Sandbox.objects.create()
    data = {'uri': request.build_absolute_uri('/api/sandboxes/'+sandbox.uuid),
            'sandbox_id': sandbox.uuid, 'checksums': {}}
    for csum in sorted(checksums):
        csum_data = data['checksums'][csum] = {}
        qs = SandboxFile.objects.filter(checksum=csum)
        if qs and qs[0].uploaded:
            csum_data['needs_upload'] = False
        else:
            if qs:
                sandbox_file = qs[0]
            else:
                sandbox_file = SandboxFile.objects.create(checksum=csum, created_by=request.client)
            sandbox_file.sandboxes.add(sandbox)
            csum_data['needs_upload'] = True
            csum_data['url'] = request.build_absolute_uri('/api/sandboxes/%s/%s'%(sandbox.uuid, csum))
    return data


@chef_api(admin=True)
def sandbox_update(request, sandbox_id):
    try:
        sandbox = Sandbox.objects.get(uuid=sandbox_id)
    except Sandbox.DoesNotExist:
        raise ChefAPIError(404, 'Sandbox not found')
    if request.json['is_completed']:
        sandbox.commit()
    return {}


@chef_api(admin=True)
def sandbox_upload(request, sandbox_id, checksum):
    try:
        sandbox = Sandbox.objects.get(uuid=sandbox_id)
    except Sandbox.DoesNotExist:
        print sandbox_id
        print Sandbox.objects.values()
        raise ChefAPIError(404, 'Sandbox not found')
    try:
        sandbox_file = SandboxFile.objects.get(checksum=checksum)
    except SandboxFile.DoesNotExist:
        raise ChefAPIError(404, 'Invalid upload target')
    if sandbox_file.uploaded:
        raise ChefAPIError(500, 'Duplicate upload')
    if sandbox_file.created_by_id != request.client.id:
        raise ChefAPIError(403, 'Upload client mismatch')
    if hashlib.md5(request.raw_post_data).hexdigest() != checksum:
        raise ChefAPIError(500, 'Checksum mismatch')
    update(sandbox_file, content_type=request.META['CONTENT_TYPE'])
    sandbox_file.write(sandbox, request.raw_post_data)
    return {'uri': request.build_absolute_uri('/api/sandboxes/%s/%s'%(sandbox_id, checksum))}


@csrf_exempt
def sandbox(request, sandbox_id=None, checksum=None):
    if not sandbox_id and not checksum:
        if request.method == 'POST':
            return sandbox_create(request)
    elif not checksum:
        if request.method == 'PUT':
            return sandbox_update(request, sandbox_id)
    else:
        if request.method == 'PUT':
            return sandbox_upload(request, sandbox_id, checksum)
    raise Http404
