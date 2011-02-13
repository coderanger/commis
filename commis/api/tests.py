import StringIO
import urllib2

from django.test import TestCase
import chef
from chef.rsa import Key, SSLError

from commis.api.models import Client

class TestChefAPI(chef.ChefAPI):
    fake_url = 'http://localhost'

    def __init__(self, testclient, *args, **kwargs):
        if 'url' in kwargs:
            kwargs['url'] = self.fake_url
        else:
            args = (self.fake_url,) + args
        super(TestChefAPI, self).__init__(*args, **kwargs)
        self.testclient = testclient

    def _request(self, request):
        args = {'path': request.get_full_url()[len(self.fake_url):]}
        if request.has_data():
            args['data'] = request.get_data()
        if request.has_header('Content-Type'):
            args['content_type'] = request.get_header('Content-Type')
        for key, value in request.header_items():
            args['HTTP_'+key.upper().replace('-', '_')] = value
        resp = getattr(self.testclient, request.get_method().lower())(**args)
        if resp.status_code != 200:
            raise urllib2.HTTPError(request.get_full_url(), resp.status_code, '', resp, StringIO.StringIO(resp.content))
        return resp.content


class ClientTestCase(TestCase):
    def test_create(self):
        c = Client.objects.create(name='test_1')
        self.assertTrue(c.key)
        self.assertTrue(c.key.public_export())
        self.assertTrue(c.key.private_export())

        c2 = Client.objects.get(name='test_1')
        self.assertTrue(c2.key)
        self.assertTrue(c2.key.public_export())
        self.assertRaises(SSLError, c2.key.private_export)


class ChefTestCase(TestCase):
    def _pre_setup(self):
        super(ChefTestCase, self)._pre_setup()
        self._client = Client.objects.create(name='unittest', admin=True)
        self.api = TestChefAPI(self.client, self._client.key, self._client.name)
        self.api.__enter__()

    def _post_teardown(self):
        self.api.__exit__(None, None, None)
        super(ChefTestCase, self)._post_teardown()


class ClientAPITestCase(ChefTestCase):
    def test_list(self):
        clients = chef.Client.list()
        self.assertTrue('unittest' in clients)

    def test_list_fail(self):
        api = TestChefAPI(self.client, Key.generate(2048), self._client.name)
        self.assertRaises(chef.ChefError, chef.Client.list, api=api)
