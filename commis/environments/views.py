from commis.generic_views import CommisAPIViewBase, api
from commis.cookbooks.models import Cookbook


class EnvironmentAPIView(CommisAPIViewBase):
    app_label = 'environments'

    @api('POST', url=r'(?P<name>[^/]+)')
    def create(self, request, name):
        # We actually don't use `name` here as it should always be _default
        # when not using Chef's environments feature.
        data = {}
        for obj in Cookbook.objects.all():
            data[obj.name] = obj.to_dict(request)
        return data
