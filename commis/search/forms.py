from django import forms
from django.utils.translation import ugettext_lazy as _

from commis.data_bags.models import DataBag
from commis.search.query_transformer import transform_query, execute_query, DEFAULT_INDEXES
from commis.utils.dict import flatten_dict

class SearchForm(forms.Form):
    index = forms.ChoiceField(choices=(), required=False)
    q = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        size = kwargs.pop('size', 0)
        super(SearchForm, self).__init__(*args, **kwargs)
        indexes = {}
        for name, model in DEFAULT_INDEXES.iteritems():
            indexes[name] = model._meta.verbose_name.capitalize()
        for name in DataBag.objects.values_list('name', flat=True):
            if name not in indexes:
                indexes[name] = name.capitalize()
        self.fields['index'].choices = sorted(indexes.iteritems())
        # If the query is too big to see, scale up to field (capped at 150)
        if 'q' in self.data and len(self.data['q']) > size - 10:
            size = min(len(self.data['q']) + 20, 150)
        if size:
            self.fields['q'].widget.attrs['size'] = size
        self._sqs = None

    def clean_q(self):
        if self.cleaned_data['q']:
            # No query isn't error, but just pass through
            try:
                self.cleaned_data['q'], self.cleaned_data['q_fields'] = transform_query(self.cleaned_data['q'])
            except Exception:
                raise forms.ValidationError(_('Invalid query'))
        return self.cleaned_data['q']

    def clean_index(self):
        if not self.cleaned_data['index']:
            return 'node'
        return self.cleaned_data['index']

    def is_searchable(self):
        return self.is_valid() and self.cleaned_data['q']

    def _run_search(self):
        if self._sqs is None and self.is_searchable():
            self._sqs = execute_query(self.cleaned_data['index'], self.cleaned_data['q'])

    @property
    def results(self):
        self._run_search()
        return self._sqs

    @property
    def table_header(self):
        return self.cleaned_data['q_fields']

    @property
    def table(self):
        for row in self.results:
            table_row = {
                'obj': row.object,
                'url': row.object.get_absolute_url(),
                'data': [],
            }
            data = flatten_dict(row.object.to_search())
            for name in self.cleaned_data['q_fields']:
                values = [unicode(v) for v in data.get(name, ())]
                table_row['data'].append(' '.join(values))
            yield table_row
