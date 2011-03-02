from haystack.backends import solr_backend

class SearchBackend(solr_backend.SearchBackend):
    def setup(self):
        super(SearchBackend, self).setup()

    def build_schema(self, fields):
        content_field_name, schema_fields = super(SearchBackend, self).build_schema(fields)
        for field in schema_fields:
            if field['type'] == 'text':
                field['type'] = 'text_ws'
        return content_field_name, schema_fields


class SearchQuery(solr_backend.SearchQuery):
    def __init__(self, site=None, backend=None):
        super(SearchQuery, self).__init__(backend=backend)

        if backend is not None:
            self.backend = backend
        else:
            self.backend = SearchBackend(site=site)
