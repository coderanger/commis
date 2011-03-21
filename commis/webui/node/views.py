from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from commis.api.node.models import Node
from commis.webui.node.forms import NodeForm

def index(request):
    return TemplateResponse(request, 'commis/node/index.html', {
        'opts': Node._meta,
        'objects': Node.objects.all(),
    })


def create(request):
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Created node %s'%form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('commis-webui-node-index'))
    else:
        form = NodeForm()
    return TemplateResponse(request, 'commis/node/create.html', {
        'opts': Node._meta,
        'obj': Node(),
        'form_info': {
            'form': form,
            'form_id': 'create_node',
            'submit_id': 'create_node_button',
            'submit_name': 'Create Node',
        },
    })


def show(request, name):
    pass


def edit(request, name):
    pass


def delete(request, name):
    pass
