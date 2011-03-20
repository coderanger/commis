from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

from commis.webui.utils import get_deleted_objects

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
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = UserChangeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited user %s'%form.cleaned_data['username'])
            return HttpResponseRedirect(reverse('commis-webui-user-show', args=[user.username]))
    else:
        form = UserChangeForm()

    return TemplateResponse(request, 'commis/user/edit.html', {'cur_user': user, 'form': form})


def delete(request, username):
    user = get_object_or_404(User, username=username)
    if request.POST: # The user has already confirmed the deletion.
        deleted_objects, perms_needed, protected = get_deleted_objects(user, request)
        if perms_needed:
            raise PermissionDenied
        user.delete()
        messages.success(request, _('Deleted user %s')%user.username)
        return HttpResponseRedirect(reverse('commis-webui-user-index'))
    return TemplateResponse(request, 'commis/user/delete.html', {'object': user})
