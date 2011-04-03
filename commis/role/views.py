from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api
from commis.role.models import Role

class RoleAPIView(CommisAPIView):
    model = Role
