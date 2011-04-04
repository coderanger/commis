from __future__ import absolute_import
import collections

from django import template
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode

from commis.webui.utils import get_deleted_objects

register = template.Library()

@register.simple_tag(takes_context=True)
def commis_nav_item(context, name, view_name):
    request = context['request']
    url = reverse(view_name)
    active = request.path_info.startswith(url)
    return '<li%s><a href="%s">%s</a></li>'%(' class="active"' if active else '', url, name)


@register.inclusion_tag('commis/delete_confirmation.html', takes_context=True)
def commis_delete_confirmation(context, obj):
    request = context['request']
    opts = obj._meta
    deleted_objects, perms_needed, protected = get_deleted_objects(obj, request)
    return {
        'object': obj,
        'object_name': force_unicode(opts.verbose_name),
        'deleted_objects': deleted_objects,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
    }


@register.inclusion_tag('commis/_json.html')
def commis_json(name, obj):
    return {
        'name': name,
        'obj': obj,
        'count': 0,
    }


@register.inclusion_tag('commis/_json_tree.html', takes_context=True)
def commis_json_tree(context, key, value, parent=0):
    root_context = context.get('root_context', context)
    root_dict = root_context.dicts[0]
    root_dict['count'] += 1
    return {
        'root_context': root_context,
        'name': context['name'],
        'count': root_dict['count'],
        'key': key,
        'value': value,
        'cur_count': root_dict['count'],
        'parent': parent,
        'is_dict': isinstance(value, collections.Mapping),
        'is_list': isinstance(value, collections.Sequence) and not isinstance(value, basestring),
    }


@register.simple_tag()
def commis_run_list_class(entry):
    if entry.startswith('recipe['):
        return 'ui-state-default'
    elif entry.startswith('role['):
        return 'ui-state-highlight'
    raise ValueError('Unknown entry %s'%entry)


@register.simple_tag()
def commis_run_list_name(entry):
    return entry.split('[', 1)[1].rstrip(']')
