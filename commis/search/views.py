import csv
import itertools
from StringIO import StringIO

from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import django.utils.simplejson as json

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

    def csv_format(self, request, form):
        outf = StringIO()
        writer = csv.writer(outf)
        writer.writerow([_('name')] + form.table_header)
        for row in form.table:
            writer.writerow([unicode(row['obj'])] + row['data'])
        return HttpResponse(outf.getvalue(), mimetype='text/plain')

    def json_format(self, request, form):
        json_data = []
        for row in form.table:
            json_row = {_('name'): unicode(row['obj'])}
            for field, value in itertools.izip(form.table_header, row['data']):
                json_row[field] = value
            json_data.append(json_row)
        return HttpResponse(json.dumps(json_data), mimetype='application/json')

    def search(self, request):
        form = SearchForm(request.GET, size=70)
        format = request.GET.get('format')
        if format and form.is_searchable():
            format_cb = {
                'csv': self.csv_format,
                'json': self.json_format,
            }.get(format)
            if format_cb:
                return format_cb(request, form)
        return TemplateResponse(request, 'commis/search/search.html', {
            'form': form,
        })

    def get_urls(self):
        return patterns('',
            url(r'^$',
                self.search,
                name='commis_webui_%s' % self.get_app_label()),
        )
