from haystack.query import SearchQuerySet, SQ

from commis.api.node.models import Node
from commis.api.data_bag.models import DataBagItem
from commis.api.search.query_parser import expression

DEFAULT_INDEXES = {
    'node': Node,
}

def transform_query(index, query_text):
    qs = SearchQuerySet()
    model = DEFAULT_INDEXES.get(index)
    if model is None:
        qs = qs.models(DataBagItem).narrow('data_bag:%s'%index)
    else:
        qs = qs.models(model)
    if query_text == '*:*':
        # Shortcut for all models, this could even skip haystack entirely.
        return qs
    query = expression.parseString(query_text, parseAll=True)
    return qs.filter(_transform(query[0]))


def _transform(query):
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
        return _transform(query[0]) & _transform(query[2])
    if 'or' in query:
        return _transform(query[0]) | _transform(query[2])
    if 'not' in query:
        return ~ _transform(query[1])
    if len(query) == 1:
        return _transform(query[0])
    raise Exception
