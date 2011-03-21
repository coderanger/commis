from django import forms
from django.core.exceptions import ValidationError

from commis.api.cookbook.models import CookbookRecipe
from commis.api.node.models import Node
from commis.api.role.models import Role

class MultipleChoiceAnyField(forms.MultipleChoiceField):
    """A MultipleChoiceField with no validation."""

    def valid_value(self, *args, **kwargs):
        return True


class NodeForm(forms.ModelForm):
    run_list = MultipleChoiceAnyField()

    class Meta:
        model = Node
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(NodeForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.initial['run_list'] = [str(entry) for entry in self.instance.run_list.all()]

    def clean_run_list(self):
        run_list = self.cleaned_data['run_list']
        ret = []
        for entry in run_list:
            if '[' not in entry:
                raise ValidationError('Unparseable run list entry "%s"' % entry)
            entry_type, entry_name = entry.rstrip(']').split('[', 1)
            entry_class = {'role': Role, 'recipe': CookbookRecipe}.get(entry_type)
            if entry_class is None:
                raise ValidationError('Unknown run list entry type "%s"' % entry_type)
            if not entry_class.objects.filter(name=entry_name).exists() or 1:
                raise ValidationError('Unknown %s "%s"' % (entry_class._meta.verbose_name, entry_name))
            ret.append({'type': entry_type, 'name': entry_name})
        return ret

    def save(self, *args, **kwargs):
        node = super(NodeForm, self).save(*args, **kwargs)
        node.run_list.delete()
        for entry in self.cleaned_data['run_list']:
            node.run_list.create(**entry)
        return node
