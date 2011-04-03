from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from commis.api.decorators import chef_api
from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api
from commis.role.models import Role
from commis.utils import json

class RoleAPIView(CommisAPIView):
    model = Role

    @api('POST', admin=True)
    def create(self, request):
        if Role.objects.filter(name=request.json['name']).exists():
            raise ChefAPIError(409, 'Role %s already exists', request.json['name'])
        role = Role.objects.from_dict(request.json)
        data = {'uri': request.build_absolute_uri(reverse('role_get', args=[role.name]))}
        return HttpResponse(json.dumps(data), status=201)

    @api('PUT', admin=True)
    def update(self, request, name):
        if request.json['name'] != name:
            raise ChefAPIError(500, 'Name mismatch')
        if not Role.objects.filter(name=name).exists():
            raise ChefAPIError(404, 'Role %s not found', name)
        return Role.objects.from_dict(request.json)

    @api('DELETE', admin=True)
    def delete(self, request, name):
        try:
            role = Role.objects.get(name=name)
        except Role.DoesNotExist:
            raise ChefAPIError(404, 'Role %s not found', name)
        role.delete()
        return role


@chef_api()
def role_list(request):
    data = {}
    for role in Role.objects.all():
        data[role.name] = request.build_absolute_uri(reverse('role_get', args=[role.name]))
    return data

@chef_api(admin=True)
def role_create(request):
    if Role.objects.filter(name=request.json['name']).exists():
        raise ChefAPIError(409, 'Role %s already exists', request.json['name'])
    role = Role.objects.from_dict(request.json)
    data = {'uri': request.build_absolute_uri(reverse('role_get', args=[role.name]))}
    return HttpResponse(json.dumps(data), status=201)


@chef_api()
def role_get(request, name):
    try:
        role = Role.objects.get(name=name)
    except Role.DoesNotExist:
        raise ChefAPIError(404, 'Role %s not found', name)
    return role


@chef_api(admin=True)
def role_update(request, name):
    if request.json['name'] != name:
        raise ChefAPIError(500, 'Name mismatch')
    if not Role.objects.filter(name=name).exists():
        raise ChefAPIError(404, 'Role %s not found', name)
    return Role.objects.from_dict(request.json)


@chef_api(admin=True)
def role_delete(request, name):
    try:
        role = Role.objects.get(name=name)
    except Role.DoesNotExist:
        raise ChefAPIError(404, 'Role %s not found', name)
    role.delete()
    return role


@csrf_exempt
def role(request, name=None):
    if not name:
        if request.method == 'GET':
            return role_list(request)
        if request.method == 'POST':
            return role_create(request)
    else:
        if request.method == 'GET':
            return role_get(request, name)
        if request.method == 'PUT':
            return role_update(request, name)
        if request.method == 'DELETE':
            return role_delete(request, name)
    raise Http404
