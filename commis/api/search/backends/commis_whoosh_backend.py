from haystack.backends import whoosh_backend
from whoosh.analysis import SimpleAnalyzer
from whoosh.fields import TEXT
from whoosh.qparser.common import rcompile
from whoosh.qparser.default import QueryParser
from whoosh.qparser.plugins import (BoostPlugin, OperatorsPlugin, FieldsPlugin,
    GroupPlugin, PhrasePlugin, RangePlugin, SingleQuotesPlugin, WildcardPlugin)

class CommisWildcardPlugin(WildcardPlugin):
    def tokens(self, parser):
        return ((CommisWildcardPlugin.Wild, 1), )

    class Wild(WildcardPlugin.Wild):
        # Any number of chars, followed by at least one question mark or
        # star, followed by any number of chars
        # \u055E = Armenian question mark
        # \u061F = Arabic question mark
        # \u1367 = Ethiopic question mark
        expr = rcompile(u"[^\\s()'\"]*[*?\u055E\u061F\u1367][^\\s()'\"]*")

plugins = (BoostPlugin, OperatorsPlugin, FieldsPlugin, GroupPlugin,
                PhrasePlugin, RangePlugin, SingleQuotesPlugin, CommisWildcardPlugin)

class SearchBackend(whoosh_backend.SearchBackend):
    def setup(self):
        super(SearchBackend, self).setup()
        self.parser = QueryParser(self.content_field_name, schema=self.schema, plugins=plugins)

    def build_schema(self, fields):
        content_field_name, schema = super(SearchBackend, self).build_schema(fields)
        for field in schema:
            if isinstance(field, TEXT):
                field.format.analyzer = SimpleAnalyzer(r'[\r\n]+', True)
        return content_field_name, schema


class SearchQuery(whoosh_backend.SearchQuery):
    def __init__(self, site=None, backend=None):
        super(SearchQuery, self).__init__(backend=backend)

        if backend is not None:
            self.backend = backend
        else:
            self.backend = SearchBackend(site=site)
