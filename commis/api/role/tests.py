import os

import chef

from commis.api import conf
from commis.api.tests import ChefTestCase
from commis.api.role.models import Role

class RoleAPITestCase(ChefTestCase):
    def test_list(self):
        Role.objects.create(name='myrole')
        self.assertIn('myrole', chef.Role.list())

    def test_create(self):
        chef.Role.create(name='myrole', run_list=['recipe[apt]'])
        role = Role.objects.get(name='myrole')
        self.assertEqual(role.run_list.count(), 1)
        self.assertEqual(role.run_list.all()[0].type, 'recipe')
        self.assertEqual(role.run_list.all()[0].name, 'apt')

    def test_get(self):
        role = Role.objects.create(name='myrole', default_data='{"test_attr": "foo"}', override_data='{"test_attr": "bar"}')
        role.run_list.create(type='recipe', name='apt')
        chef_role = chef.Role('myrole')
        self.assertEqual(chef_role.default_attributes['test_attr'], 'foo')
        self.assertEqual(chef_role.override_attributes['test_attr'], 'bar')
        self.assertEqual(chef_role.run_list, ['recipe[apt]'])

    def test_update(self):
        role = Role.objects.create(name='myrole', default_data='{"test_attr": "foo"}')
        role.run_list.create(type='recipe', name='apt')
        chef_role = chef.Role('myrole')
        chef_role.default_attributes['test_attr'] = 'bar'
        chef_role.run_list = ['role[web_server]']
        chef_role.save()
        role = Role.objects.get(name='myrole')
        self.assertEqual(role.default, {u'test_attr': u'bar'})
        self.assertEqual(role.run_list.count(), 1)
        self.assertEqual(role.run_list.all()[0].type, 'role')
        self.assertEqual(role.run_list.all()[0].name, 'web_server')

    def test_delete(self):
        Role.objects.create(name='myrole')
        chef.Role('myrole').delete()
        with self.assertRaises(Role.DoesNotExist):
            Role.objects.get(name='myrole')
