import os

from commis import conf
from commis.test import ChefTestCase
from commis.sandbox.models import SandboxFile

class SandboxAPITestCase(ChefTestCase):
    def test_create(self):
        checksums = [
            '385ea5490c86570c7de71070bce9384a',
            'f6f73175e979bd90af6184ec277f760c',
            '2e03dd7e5b2e6c8eab1cf41ac61396d5',
        ]
        input = {'checksums': dict((csum, None) for csum in checksums)}
        resp = self.api.api_request('POST', '/sandboxes', data=input)
        self.assertIn('uri', resp)
        self.assertIn('sandbox_id', resp)
        self.assertTrue(resp['sandbox_id'])
        self.assertIn('checksums', resp)
        for csum in checksums:
            self.assertIn(csum, resp['checksums'])
            self.assertIn('needs_upload', resp['checksums'][csum])
            self.assertTrue(resp['checksums'][csum]['needs_upload'])
            self.assertIn('url', resp['checksums'][csum])
            self.assertTrue(resp['checksums'][csum]['url'])

    def test_upload(self):
        checksums = [
            'ab56b4d92b40713acc5af89985d4b786', # 'abcde'
            '0fbd31a7d4febcc8ea2f84414ab95684', # 'abc\0de'
            '9fb548d26b69c60aae1cbdfe25348377', # 'abc\nde'
        ]
        input = {'checksums': dict((csum, None) for csum in checksums)}
        resp = self.api.api_request('POST', '/sandboxes', data=input)
        self.api.request('PUT', '/sandboxes/%s/ab56b4d92b40713acc5af89985d4b786'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abcde')
        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, 'pending', resp['sandbox_id'], 'a', 'b', 'ab56b4d92b40713acc5af89985d4b786')).read(), 'abcde')
        self.api.request('PUT', '/sandboxes/%s/0fbd31a7d4febcc8ea2f84414ab95684'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abc\0de')
        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, 'pending', resp['sandbox_id'], '0', 'f', '0fbd31a7d4febcc8ea2f84414ab95684')).read(), 'abc\0de')
        self.api.request('PUT', '/sandboxes/%s/9fb548d26b69c60aae1cbdfe25348377'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abc\nde')
        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, 'pending', resp['sandbox_id'], '9', 'f', '9fb548d26b69c60aae1cbdfe25348377')).read(), 'abc\nde')

        self.assertFalse(SandboxFile.objects.get(checksum='ab56b4d92b40713acc5af89985d4b786').uploaded)
        self.assertFalse(SandboxFile.objects.get(checksum='0fbd31a7d4febcc8ea2f84414ab95684').uploaded)
        self.assertFalse(SandboxFile.objects.get(checksum='9fb548d26b69c60aae1cbdfe25348377').uploaded)

    def test_commit(self):
        checksums = [
            'ab56b4d92b40713acc5af89985d4b786', # 'abcde'
            '0fbd31a7d4febcc8ea2f84414ab95684', # 'abc\0de'
            '9fb548d26b69c60aae1cbdfe25348377', # 'abc\nde'
        ]
        input = {'checksums': dict((csum, None) for csum in checksums)}
        resp = self.api.api_request('POST', '/sandboxes', data=input)
        self.api.request('PUT', '/sandboxes/%s/ab56b4d92b40713acc5af89985d4b786'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abcde')
        self.api.request('PUT', '/sandboxes/%s/0fbd31a7d4febcc8ea2f84414ab95684'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abc\0de')
        self.api.request('PUT', '/sandboxes/%s/9fb548d26b69c60aae1cbdfe25348377'%resp['sandbox_id'], headers={'Content-Type': 'text/plain'}, data='abc\nde')
        self.api.api_request('PUT', '/sandboxes/%s'%resp['sandbox_id'], data={'is_completed': True})

        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, 'a', 'b', 'ab56b4d92b40713acc5af89985d4b786')).read(), 'abcde')
        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, '0', 'f', '0fbd31a7d4febcc8ea2f84414ab95684')).read(), 'abc\0de')
        self.assertEqual(open(os.path.join(conf.COMMIS_FILE_ROOT, '9', 'f', '9fb548d26b69c60aae1cbdfe25348377')).read(), 'abc\nde')

        self.assertTrue(SandboxFile.objects.get(checksum='ab56b4d92b40713acc5af89985d4b786').uploaded)
        self.assertTrue(SandboxFile.objects.get(checksum='0fbd31a7d4febcc8ea2f84414ab95684').uploaded)
        self.assertTrue(SandboxFile.objects.get(checksum='9fb548d26b69c60aae1cbdfe25348377').uploaded)
