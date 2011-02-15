import chef
from django.http import Http404

from commis.api import conf
from commis.api.decorators import chef_api
from commis.api.exceptions import ChefAPIError
from commis.api.sandbox.models import Sandbox, SandboxFile

@chef_api(admin=True)
def sandbox_create(request):
    checksums = request.json['checksums'].keys()
    sandbox = Sandbox.objects.create()
    data = {'uri': request.build_absolute_uri('/sandboxes/'+sandbox.uuid),
            'sandbox_id': sandbox.uuid, 'checksums': {}}
    for csum in sorted(checksums):
        csum_data = data['checksums'][csum] = {}
        if SandboxFile.objects.filter(checksum=csum).exists():
            csum_data['needs_upload'] = False
        else:
            csum_data['needs_upload'] = True
            csum_data['uri'] = request.build_absolute_uri('/sandboxes/%s/%s'%(sandbox.uuid, csum))
    return data


@chef_api(admin=True)
def sandbox_update(request, sandbox_id):
    pass


@chef_api(admin=True)
def sandbox_upload(request, sandbox_id, checksum):
    pass


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
