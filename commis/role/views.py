from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api
from commis.role.models import Role

class RoleAPIView(CommisAPIView):
    model = Role

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
