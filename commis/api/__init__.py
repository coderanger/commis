import logging

logger = logging.getLogger(__name__)

class CrazyMiddleware(object):
    def process_response(self, request, response):
        logger.debug(response.content)
        return response

    def process_exception(self, request, exception):
        logger.debug(exception)
