import itertools

from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from commis.data_bag.models import DataBag
from commis.api.decorators import chef_api
from commis.exceptions import ChefAPIError
from commis.search.query_transformer import transform_query, DEFAULT_INDEXES

@chef_api()
def search_list(request):
    data = {}
    for name in itertools.chain(DEFAULT_INDEXES.iterkeys(), DataBag.objects.values_list('name', flat=True)):
        data[name] = request.build_absolute_uri(reverse('search_get', args=[name]))
    return data


@chef_api()
def search_get(request, name):
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
        


@csrf_exempt
def search(request, name=None):
    if not name:
        if request.method == 'GET':
            return search_list(request)
    else:
        if request.method == 'GET':
            return search_get(request, name)
    raise Http404
