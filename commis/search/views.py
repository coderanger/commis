import itertools

from django.conf.urls.defaults import patterns, url
from django.template.response import TemplateResponse

from commis.data_bags.models import DataBag
from commis.generic_views import CommisAPIViewBase, api, CommisViewBase
from commis.exceptions import ChefAPIError
from commis.search.forms import SearchForm
from commis.search.query_transformer import DEFAULT_INDEXES

class SearchAPIView(CommisAPIViewBase):
    app_label = 'search'

    @api('GET')
    def list(self, request):
        data = {}
        for name in itertools.chain(DEFAULT_INDEXES.iterkeys(), DataBag.objects.values_list('name', flat=True)):
            data[name] = self.reverse(request, 'get', name)
        return data

    @api('GET')
    def get(self, request, name):
        args = {'index': name, 'q': request.GET.get('q', '*:*')}
        form = SearchForm(args)
        if not form.is_searchable():
            if form['index'].errors:
                raise ChefAPIError(404, 'Index %s not found', name)
            raise ChefAPIError(500, 'Invalid search')
        rows = int(request.GET.get('rows', 20))
        start = int(request.GET.get('start', 0))
        rows = [result.object for result in form.results[start:start+rows]]
        return {
            'total': form.results.count(),
            'start': start,
            'rows': rows,
        }


class SearchView(CommisViewBase):
    app_label = 'search'

    def search(self, request):
        return TemplateResponse(request, 'commis/search/search.html', {
            'form': SearchForm(request.GET, size=70),
        })

    def get_urls(self):
        return patterns('',
            url(r'^$',
                self.search,
                name='commis_webui_%s' % self.get_app_label()),
        )
