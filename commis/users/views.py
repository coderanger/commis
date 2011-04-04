from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from commis.generic_views import CommisView

class UserView(CommisView):
    model = User
    create_form = UserCreationForm
    edit_form = UserChangeForm
    app_label = 'users'
    search_key = 'username'

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        return patterns('',
            url(r'^login/$', 'django.contrib.auth.views.login', kwargs={'template_name': 'commis/users/login.html'}),
            url(r'^logout/$', 'django.contrib.auth.views.logout'),
        ) + super(UserView, self).get_urls()
