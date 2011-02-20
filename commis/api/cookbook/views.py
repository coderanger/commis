import chef
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api import conf
from commis.api.decorators import chef_api
from commis.api.exceptions import ChefAPIError
from commis.api.cookbook.models import Cookbook, CookbookFile
from commis.api.sandbox.models import SandboxFile

@chef_api()
def cookbook_index(request):
    data = {}
    for name in Cookbook.objects.values_list('name', flat=True):
        data[name] = request.build_absolute_uri('/api/cookbooks/'+name)
    return data


@chef_api()
def cookbook_get(request, name):
    versions = Cookbook.objects.filter(name=name).values_list('version', flat=True)
    if not versions:
        raise ChefAPIError(404, 'Cookbook %s not found', name)
    return {name: versions}


@chef_api()
def cookbook_get_version(request, name, version):
    try:
        cookbook = Cookbook.objects.get(name=name, version=version)
    except Cookbook.DoesNotExist:
        raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
    return cookbook.to_dict(request)


@chef_api(admin=True)
def cookbook_update(request, name, version):
    cookbook = Cookbook.objects.from_dict(request.json)
    return cookbook.to_dict(request)


@chef_api(admin=True)
def cookbook_delete(request, name, version):
    qs = Cookbook.objects.filter(name=name, version=version)
    if not qs.exists():
        raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
    qs.delete()
    return {}


@chef_api()
def cookbook_file(request, name, version, checksum):
    qs = CookbookFile.objects.select_related('file').filter(cookbook__name=name, cookbook__version=version, file__checksum=checksum, file__uploaded=True)
    if not qs:
        raise ChefAPIError(404, 'File not found')
    cookbook_file = qs[0]
    response = HttpResponse(open(cookbook_file.file.path, 'rb').read(), content_type=cookbook_file.file.content_type)
    return response


@csrf_exempt
def cookbook(request, name=None, version=None, checksum=None):
    if not name and not version and not checksum:
        if request.method == 'GET':
            return cookbook_index(request)
    elif not version and not checksum:
        if request.method == 'GET':
            return cookbook_get(request, name)
    elif not checksum:
        if request.method == 'GET':
            return cookbook_get_version(request, name, version)
        if request.method == 'PUT':
            return cookbook_update(request, name, version)
        if request.method == 'DELETE':
            return cookbook_delete(request, name, version)
    else:
        if request.method == 'GET':
            return cookbook_file(request, name, version, checksum)
    raise Http404
