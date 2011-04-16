from __future__ import absolute_import

from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
@stringfilter
def commis_status_short_uptime(uptime):
    return ' '.join(uptime.split()[0:2])
