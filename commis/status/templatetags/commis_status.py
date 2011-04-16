from __future__ import absolute_import
import datetime

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _, ungettext

register = template.Library()

@register.filter
@stringfilter
def commis_status_short_uptime(uptime):
    return ' '.join(uptime.split()[0:2])


@register.inclusion_tag('commis/status/_last_checkin.html')
def commis_status_last_checkin(ohai_time):
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(ohai_time)

    # Compute the CSS class for the cell
    if delta >= datetime.timedelta(days=1):
        status_class = 'error'
    elif delta >= datetime.timedelta(hours=1):
        status_class = 'warning'
    else:
        status_class = ''
    
    hours = delta.seconds // 3600
    hours_text = ungettext('%(hours)s hour', '%(hours)s hours', hours) % {'hours': hours}
    minutes = delta.seconds // 60
    minutes_text = ungettext('%(minutes)s minute', '%(minutes)s minutes', minutes) % {'minutes': minutes}

    # Short form of the delta
    if delta.days > 2:
        delta_short = _('> %(days)s days ago') % {'days': delta.days}
    elif hours:
        delta_short = _('> %(hours_text)s ago') % {'hours_text': hours_text}
    elif minutes < 1:
        delta_short = _('< 1 minute ago')
    else:
        delta_short = _('%(minutes_text)s ago') % {'minutes_text': minutes_text}

    # Long form of the delta
    if hours:
        delta_long = _('%(hours_text)s, %(minutes_text)s ago') % {'hours_text': hours_text, 'minutes_text': minutes_text}
    else:
        delta_long = _('%(minutes_text)s ago') % {'minutes_text': minutes_text}
    return {
        'ohai_time': ohai_time,
        'status_class': status_class,
        'delta_short': delta_short,
        'delta_long': delta_long,
    }
