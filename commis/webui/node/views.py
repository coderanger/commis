from django.template.response import TemplateResponse

from commis.api.node.models import Node

def index(request):
    return TemplateResponse(request, 'commis/node/index.html', {
        'opts': Node._meta,
        'objects': Node.objects.all(),
    })


def create(request):
    pass


def show(request, name):
    pass


def edit(request, name):
    pass


def delete(request, name):
    pass
