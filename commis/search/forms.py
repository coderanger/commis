from django import forms
from django.utils.translation import ugettext_lazy as _

from commis.data_bags.models import DataBag
from commis.search.query_transformer import transform_query, execute_query, DEFAULT_INDEXES

class SearchForm(forms.Form):
    index = forms.ChoiceField(choices=(), required=False)
    q = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        indexes = {}
        for name, model in DEFAULT_INDEXES.iteritems():
            indexes[name] = model._meta.verbose_name.capitalize()
        for name in DataBag.objects.values_list('name', flat=True):
            if name not in indexes:
                indexes[name] = name.capitalize()
        self.fields['index'].choices = sorted(indexes.iteritems())
        self._sqs = None

    def clean_q(self):
        if self.cleaned_data['q']:
            # No query isn't error, but just pass through
            try:
                self.cleaned_data['q'] = transform_query(self.cleaned_data['q'])
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
        print '%r %r'%(self.cleaned_data['index'], self.cleaned_data['q'])
        if self._sqs is None and self.is_searchable():
            print 'RUNNING SEARCH'
            self._sqs = execute_query(self.cleaned_data['index'], self.cleaned_data['q'])

    @property
    def results(self):
        self._run_search()
        return self._sqs
