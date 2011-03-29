import shutil
import StringIO
import tempfile
import urllib2
import urlparse

from django.test import TestCase
import chef

from commis import conf
from commis.api.models import Client


class TestChefAPI(chef.ChefAPI):
    fake_url = 'http://localhost/api'

    def __init__(self, testclient, *args, **kwargs):
        if 'url' in kwargs:
            kwargs['url'] = self.fake_url
        else:
            args = (self.fake_url,) + args
        super(TestChefAPI, self).__init__(*args, **kwargs)
        self.testclient = testclient

    def _request(self, method, url, data, headers):
        parsed_url = urlparse.urlparse(url)
        args = {'path': parsed_url.path}
        if parsed_url.query:
            args['path'] += '?' + parsed_url.query
        if data:
            args['data'] = data
        for key, value in headers.iteritems():
            args['HTTP_'+key.upper().replace('-', '_')] = value
        if 'HTTP_CONTENT_TYPE' in args:
            args['content_type'] = args['HTTP_CONTENT_TYPE']
        resp = getattr(self.testclient, method.lower())(**args)
        if not (200 <= resp.status_code < 300):
            raise urllib2.HTTPError(url, resp.status_code, '', resp, StringIO.StringIO(resp.content))
        return resp.content


class ChefTestCase(TestCase):
    def setUp(self):
        super(ChefTestCase, self).setUp()
        self.old_file_root = conf.COMMIS_FILE_ROOT
        conf.COMMIS_FILE_ROOT = tempfile.mkdtemp()

        self._client = Client.objects.create(name='unittest', admin=True)
        self.api = TestChefAPI(self.client, self._client.key, self._client.name)
        self.api.__enter__()

    def tearDown(self):
        self.api.__exit__(None, None, None)

        shutil.rmtree(conf.COMMIS_FILE_ROOT)
        conf.COMMIS_FILE_ROOT = self.old_file_root
        super(ChefTestCase, self).tearDown()
