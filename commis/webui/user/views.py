from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

def index(request):
    return TemplateResponse(request, 'commis/user/index.html', {'users': User.objects.all()})


def create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Created user %s'%form.cleaned_data['username'])
            return HttpResponseRedirect(reverse('commis-webui-user-index'))
    else:
        form = UserCreationForm()

    return TemplateResponse(request, 'commis/user/create.html', {'form': form})


def show(request, username):
    user = get_object_or_404(User, username=username)
    return TemplateResponse(request, 'commis/user/show.html', {'cur_user': user})


def edit(request, username):
    pass


def delete(request, username):
    pass
