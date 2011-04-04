from commis.generic_views import CommisAPIView
from commis.role.models import Role

class RoleAPIView(CommisAPIView):
    model = Role
