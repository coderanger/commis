from django.http import HttpResponse

from commis.exceptions import ChefAPIError
from commis.generic_views import CommisAPIView, api
from commis.cookbook.models import Cookbook, CookbookFile

class CookbookAPIView(CommisAPIView):
    model = Cookbook

    @api('GET')
    def get(self, request, name):
        versions = Cookbook.objects.filter(name=name).values_list('version', flat=True)
        if not versions:
            raise ChefAPIError(404, 'Cookbook %s not found', name)
        return {name: versions}

    @api('GET')
    def version(self, request, name, version):
        try:
            cookbook = Cookbook.objects.get(name=name, version=version)
        except Cookbook.DoesNotExist:
            raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
        return cookbook.to_dict(request)

    @api('PUT', admin=True)
    def update(self, request, name, version):
        cookbook = Cookbook.objects.from_dict(request.json)
        return cookbook.to_dict(request)

    @api('DELETE', admin=True)
    def delete(self, request, name, version):
        qs = Cookbook.objects.filter(name=name, version=version)
        if not qs.exists():
            raise ChefAPIError(404, 'Cookbook %s@%s not found', name, version)
        qs.delete()
        return {}

    @api('GET', '{name}/{version}/files/{checksum}')
    def file(self, request, name, version, checksum):
        qs = CookbookFile.objects.select_related('file').filter(cookbook__name=name, cookbook__version=version, file__checksum=checksum, file__uploaded=True)
        if not qs:
            raise ChefAPIError(404, 'File not found')
        cookbook_file = qs[0]
        response = HttpResponse(open(cookbook_file.file.path, 'rb').read(), content_type=cookbook_file.file.content_type)
        return response
