import logging

logger = logging.getLogger(__name__)

class LogOutputMiddleware(object):
    def process_response(self, request, response):
        logger.info(response.content)
        return response

    def process_exception(self, request, exception):
        logger.info(exception)
