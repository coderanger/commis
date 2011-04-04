from commis.generic_views import CommisAPIView
from commis.roles.models import Role

class RoleAPIView(CommisAPIView):
    model = Role
