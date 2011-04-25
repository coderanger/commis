import csv
import itertools
from StringIO import StringIO

from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

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
        form = SearchForm(request.GET, size=70)
        format = request.GET.get('format')
        if format and form.is_searchable():
            if format == 'csv':
                outf = StringIO()
                writer = csv.writer(outf)
                writer.writerow([_('name')] + form.table_header)
                for row in form.table:
                    writer.writerow([unicode(row['obj'])] + row['data'])
                return HttpResponse(outf.getvalue(), mimetype='text/plain')
            elif format == 'json':
                pass
        return TemplateResponse(request, 'commis/search/search.html', {
            'form': form,
        })

    def get_urls(self):
        return patterns('',
            url(r'^$',
                self.search,
                name='commis_webui_%s' % self.get_app_label()),
        )
