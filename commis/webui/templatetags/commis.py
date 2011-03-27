from __future__ import absolute_import
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


@register.inclusion_tag('commis/jsoneditor.html')
def commis_jsoneditor(json):
    return {'json': json}


@register.inclusion_tag('commis/jsoneditor_includes.html', takes_context=True)
def commis_jsoneditor_includes(context):
    return context


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
