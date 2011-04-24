from haystack.query import SearchQuerySet, SQ

from commis.nodes.models import Node
from commis.data_bags.models import DataBagItem
from commis.search.exceptions import InvalidSearchQuery
from commis.search.query_parser import expression

DEFAULT_INDEXES = {
    'node': Node,
}

def transform_query(query_text):
    if query_text == '*:*':
         return query_text, []
    if ':' not in query_text:
        # Use simple query mode
        query_text = ' AND '.join('%s:*'%field for field in query_text.split())
    query = expression.parseString(query_text, parseAll=True)
    fields = []
    transformed_query = _transform(query[0], fields)
    return transformed_query, fields


def execute_query(index, query_text):
    qs = SearchQuerySet().order_by('id_order')
    model = DEFAULT_INDEXES.get(index)
    if model is None:
        qs = qs.models(DataBagItem).narrow('data_bag:%s'%index)
    else:
        qs = qs.models(model)
    if query_text == '*:*':
        # Shortcut for all models, this could even skip haystack entirely.
        return qs
    return qs.filter(query_text)


def _transform(query, fields):
    if 'field' in query and query['field'] not in fields and '*' not in query['field']:
        fields.append(query['field'])
    if 'value' in query:
        return SQ(content='%s__=__%s'%(query['field'], query['value']))
    if 'incl_range' in query:
        lower = query['incl_range']['lower']
        upper = query['incl_range']['upper']
        if lower == '*' and upper == '*':
            # Shortcut for [* TO *]
            return SQ(content='%s__=__*'%(query['field']))
        return SQ(text__range=['%s__=__%s'%(query['field'], lower), 
                                  '%s__=__%s'%(query['field'], upper)])
    elif 'excl_range' in query:
        lower = query['excl_range']['lower']
        upper = query['excl_range']['upper']
        return ~SQ(text__range=['%s__=__%s'%(query['field'], lower), 
                                   '%s__=__%s'%(query['field'], upper)])
    if 'and' in query:
        return _transform(query[0], fields) & _transform(query[2], fields)
    if 'or' in query:
        return _transform(query[0], fields) | _transform(query[2], fields)
    if 'not' in query:
        return ~ _transform(query[1], fields)
    if len(query) == 1:
        return _transform(query[0], fields)
    raise InvalidSearchQuery
