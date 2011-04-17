import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.http import urlquote

from commis.exceptions import InsuffcientPermissions

logger = logging.getLogger(__name__)

class LogOutputMiddleware(object):
    def process_response(self, request, response):
        logger.debug(response.content)
        return response

    def process_exception(self, request, exception):
        logger.info(exception)


class PermissionsMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, InsuffcientPermissions):
            if request.user.is_authenticated():
                # Logged in, send back a nice page
                    return TemplateResponse(request, 'commis/403.html', {})
            else:
                # Not logged in, redirect
                return HttpResponseRedirect(request.build_absolute_uri(reverse('django.contrib.auth.views.login') + '?next=' + urlquote(request.get_full_path())))
