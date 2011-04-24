from __future__ import absolute_import

from django import template
from commis.utils.dict import flatten_dict

register = template.Library()

@register.filter
def commis_search_row_get(row, field_name):
    if not getattr(row, '_flattened_data', None):
        row._flattened_data = flatten_dict(row.object.to_search())
    for key, values in row._flattened_data.iteritems():
        if field_name == key:
            return values
    return []
