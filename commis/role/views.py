from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api
from commis.role.models import Role

class RoleAPIView(CommisAPIView):
    model = Role

    @api('DELETE', admin=True)
    def delete(self, request, name):
        try:
            role = Role.objects.get(name=name)
        except Role.DoesNotExist:
            raise ChefAPIError(404, 'Role %s not found', name)
        role.delete()
        return role
