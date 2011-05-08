from django import forms
from django.core.exceptions import ValidationError

from commis.data_bags.models import DataBag, DataBagItem
from commis.utils import json

class DataBagForm(forms.ModelForm):
    class Meta:
        model = DataBag
        fields = ('name',) 


class DataBagItemForm(forms.ModelForm):
    class Meta:
        model = DataBagItem
        fields = ('name', 'data') 

    def __init__(self, bag, *args, **kwargs):
        super(DataBagItemForm, self).__init__(*args, **kwargs)
        self.__bag = bag

    def save(self, *args, **kwargs):
        self.instance.bag = self.__bag
        return super(DataBagItemForm, self).save(*args, **kwargs)

    def clean_data(self):
        try:
            json.loads(self.cleaned_data['data'])
        except ValueError, e:
            raise ValidationError(str(e))
        return self.cleaned_data['data']
