import datetime
import StringIO
import urllib2
import urlparse

from django.test import TestCase
import chef
from chef.auth import sign_request
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

    def _request(self, method, url, data, headers):
        args = {'path': urlparse.urlparse(url).path}
        if data:
            args['data'] = data
        if 'Content-Type' in headers:
            args['content_type'] = headers['Content-Type']
        for key, value in headers.iteritems():
            args['HTTP_'+key.upper().replace('-', '_')] = value
        resp = getattr(self.testclient, method.lower())(**args)
        if resp.status_code != 200:
            raise urllib2.HTTPError(url, resp.status_code, '', resp, StringIO.StringIO(resp.content))
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


class APITestCase(ChefTestCase):
    def sign_request(self, path, **kwargs):
        d = dict(key=self.api.key, http_method='GET',
            path=self.api.parsed_url.path+path.split('?', 1)[0], body=None,
            host=self.api.parsed_url.netloc, timestamp=datetime.datetime.utcnow(),
            user_id=self.api.client)
        d.update(kwargs)
        return sign_request(**d)

    def test_good(self):
        path = '/clients'
        auth_headers = self.sign_request(path)
        headers = {}
        for key, value in auth_headers.iteritems():
            headers['HTTP_'+key.upper().replace('-', '_')] = value
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 200)

    def test_bad_timestamp(self):
        path = '/clients'
        auth_headers = self.sign_request(path, timestamp=datetime.datetime(2000, 1, 1))
        headers = {}
        for key, value in auth_headers.iteritems():
            headers['HTTP_'+key.upper().replace('-', '_')] = value
        response = self.client.get(path, **headers)
        self.assertContains(response, 'clock', status_code=401)

    def test_no_sig(self):
        path = '/clients'
        auth_headers = self.sign_request(path)
        headers = {}
        for key, value in auth_headers.iteritems():
            if key.lower().startswith('x-ops-authorization'):
                continue
            headers['HTTP_'+key.upper().replace('-', '_')] = value
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 401)


class ClientAPITestCase(ChefTestCase):
    def test_list(self):
        clients = chef.Client.list()
        self.assertTrue('unittest' in clients)

    def test_list_fail(self):
        api = TestChefAPI(self.client, Key.generate(2048), self._client.name)
        self.assertRaises(chef.ChefError, chef.Client.list, api=api)