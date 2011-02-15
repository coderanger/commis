from commis.api.tests import ChefTestCase

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
            self.assertIn('uri', resp['checksums'][csum])
            self.assertTrue(resp['checksums'][csum]['uri'])
