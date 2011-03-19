from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def commis_nav_item(context, name, view_name):
    request = context['request']
    url = reverse(view_name)
    active = request.path_info.startswith(url)
    return '<li%s><a href="%s">%s</a></li>'%(' class="active"' if active else '', url, name)
