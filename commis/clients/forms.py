from django import forms

from commis.clients.models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'admin')
