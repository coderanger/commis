import itertools

from commis.data_bags.models import DataBag
from commis.generic_views import CommisAPIViewBase, api
from commis.exceptions import ChefAPIError
from commis.search.query_transformer import transform_query, DEFAULT_INDEXES

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
        if name not in DEFAULT_INDEXES and not DataBag.objects.filter(name=name).exists():
            raise ChefAPIError(404, 'Index %s not found', name)
        sqs = transform_query(name, request.GET.get('q', '*:*'))
        rows = int(request.GET.get('rows', 20))
        start = int(request.GET.get('start', 0))
        rows = [result.object for result in sqs[start:start+rows]]
        return {
            'total': sqs.count(),
            'start': start,
            'rows': rows,
        }
