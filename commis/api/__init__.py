class CrazyMiddleware(object):
    def process_response(self, request, response):
        print response.content
        return response

    def process_exception(self, request, exception):
        print exception
