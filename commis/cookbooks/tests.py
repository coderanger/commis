from commis.test import ChefTestCase

class CookbookAPITestCase(ChefTestCase):
    fixtures = ['cookbook_apt']
    maxDiff = 100000
    
    def test_list(self):
        data = self.api['/cookbooks']
        self.assertEqual(data, {'apt': 'http://testserver/api/cookbooks/apt'})

    def test_get(self):
        data = self.api['/cookbooks/apt']
        self.assertEqual(data, {'apt': ['1.0.0']})

    def test_get_version(self):
        data = self.api['/cookbooks/apt/1.0.0']
        reference = {
            'name': 'apt-1.0.0',
            'cookbook_name': 'apt',
            'version': '1.0.0',
            'json_class': 'Chef::CookbookVersion',
            'chef_type': 'cookbook_version',
            'metadata': {
                'name': 'apt',
                'version': '1.0.0',
                'maintainer': 'Opscode, Inc.',
                'maintainer_email': 'cookbooks@opscode.com',
                'license': 'Apache 2.0',
                'description': 'Configures apt and apt services and an LWRP for managing apt repositories',
                'long_description': 'Description\n===========\n\nConfigures various APT components on Debian-like systems.  Also includes a LWRP.\n\n',
                'dependencies': {
                    'ruby': [],
                },
                'recipes': {
                    'apt': 'Runs apt-get update during compile phase and sets up preseed directories',
                    'apt::cacher': 'Set up an APT cache',
                    'apt::proxy': 'Set up an APT proxy',
                 },
                'attributes': {},
                'suggestions': {},
                'platforms': {},
                'recommendations': {},
                'conflicting': {},
                'groupings': {},
                'replacing': {},
                'providing': {},
            },
            'attributes': [],
            'definitions': [],
            'files': [
                {
                    'checksum': '046661f9e728b783ea90738769219d71',
                    'name': 'apt-cacher',
                    'specificity': 'default',
                    'path': 'files/default/apt-cacher',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/046661f9e728b783ea90738769219d71',
                },
                {
                    'checksum': '3e4afb4ca7cb38b707b803cbb2a316a7',
                    'name': 'apt-cacher.conf',
                    'specificity': 'default',
                    'path': 'files/default/apt-cacher.conf',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/3e4afb4ca7cb38b707b803cbb2a316a7',
                },
                {
                    'checksum': 'a67a0204d4c54848aad67a8e9de5cad1',
                    'name': 'apt-proxy-v2.conf',
                    'specificity': 'default',
                    'path': 'files/default/apt-proxy-v2.conf',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/a67a0204d4c54848aad67a8e9de5cad1',
                },
            ],
            'libraries': [],
            'providers': [],
            'recipes': [
                {
                    'checksum': '5479013c6f17fb6e1930ea31e8fb1df5',
                    'name': 'cacher.rb',
                    'specificity': 'default',
                    'path': 'recipes/cacher.rb',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/5479013c6f17fb6e1930ea31e8fb1df5',
                },
                {
                    'checksum': '112a8c22a020417dcc1c1fd06a4312ef',
                    'name': 'default.rb',
                    'specificity': 'default',
                    'path': 'recipes/default.rb',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/112a8c22a020417dcc1c1fd06a4312ef',
                },
                {
                    'checksum': '434450082c67c354884c4b8b5db23ffb',
                    'name': 'proxy.rb',
                    'specificity': 'default',
                    'path': 'recipes/proxy.rb',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/434450082c67c354884c4b8b5db23ffb',
                },
            ],
            'resources': [
                {
                    'checksum': '33653076212a8b7737838198bbea2d72',
                    'name': 'repository.rb',
                    'specificity': 'default',
                    'path': 'resources/repository.rb',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/33653076212a8b7737838198bbea2d72',
                },
            ],
            'root_files': [
                {
                    'checksum': '3e7cc22c3f9a1a9e8708d5c2a3cd2d64',
                    'name': 'metadata.json',
                    'specificity': 'default',
                    'path': 'metadata.json',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/3e7cc22c3f9a1a9e8708d5c2a3cd2d64',
                },
                {
                    'checksum': '4d80cafd968bb603d9f1a6a9422663e4',
                    'name': 'metadata.rb',
                    'specificity': 'default',
                    'path': 'metadata.rb',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/4d80cafd968bb603d9f1a6a9422663e4',
                },
                {
                    'checksum': 'c7faa6cd1213a6afff1e59ee447b9fd0',
                    'name': 'README.md',
                    'specificity': 'default',
                    'path': 'README.md',
                    'url': 'http://testserver/api/cookbooks/apt/1.0.0/files/c7faa6cd1213a6afff1e59ee447b9fd0',
                },
            ],
            'templates': [],
        }
        self.assertEqual(data, reference)
