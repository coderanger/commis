from django import forms
from django.utils.translation import ugettext_lazy as _

from commis.clients.models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'admin')

    def save(self, commit=True):
        ret = super(ClientForm, self).save(commit)
        if not self.instance.key:
            self.instance.generate_key()
        return ret

class ClientEditForm(ClientForm):
    rekey = forms.BooleanField(
        label=_('Regenerate private key'),
        required=False,
        help_text=_('Generate a new key for this client. This will invalidate the current key.')
    )

    def save(self, commit=True):
        if self.cleaned_data['rekey']:
            self.instance.generate_key()
        return super(ClientEditForm, self).save(commit)
