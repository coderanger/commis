from commis.generic_views import CommisAPIView, CommisView
from commis.roles.forms import RoleForm
from commis.roles.models import Role

class RoleAPIView(CommisAPIView):
    model = Role

class RoleView(CommisView):
    model = Role
    form = RoleForm
