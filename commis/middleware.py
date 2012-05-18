import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.http import urlquote

from commis.exceptions import InsuffcientPermissions
from commis.utils import json

logger = logging.getLogger(__name__)

class LogOutputMiddleware(object):
    def process_response(self, request, response):
        # We're primarily interested in debuggin API output.
        # Non-API URLs are typically hit by a user who will see the debug info
        # in the browser. API can't do that!
        if request.path.startswith("/api"):
            content = response.content
            # JSON responses (caveat: this is probably all of them...) should
            # get pretty-printed
            if response['content-type'] == 'application/json':
                obj = json.loads(content)
                # And responses containing a top level traceback key should
                # also pretty-print that value.
                traceback = obj and obj.pop('traceback', None)
                if traceback is not None:
                    logger.debug(traceback)
                content = json.dumps(obj, indent=4)
            logger.debug(content)
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
