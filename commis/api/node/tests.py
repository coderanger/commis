import os

import chef

from commis.api import conf
from commis.api.tests import ChefTestCase
from commis.api.node.models import Node

class NodeAPITestCase(ChefTestCase):
    fixtures = ['cookbook_apt']

    def test_list(self):
        Node.objects.create(name='mynode')
        self.assertIn('mynode', chef.Node.list())

    def test_create(self):
        chef.Node.create(name='mynode', run_list=['recipe[apt]'])
        node = Node.objects.get(name='mynode')
        self.assertEqual(node.run_list.count(), 1)
        self.assertEqual(node.run_list.all()[0].type, 'recipe')
        self.assertEqual(node.run_list.all()[0].name, 'apt')

    def test_get(self):
        node = Node.objects.create(name='mynode', normal_data='{"test_attr": "foo"}')
        node.run_list.create(type='recipe', name='apt')
        chef_node = chef.Node('mynode')
        self.assertEqual(chef_node['test_attr'], 'foo')
        self.assertEqual(chef_node.run_list, ['recipe[apt]'])

    def test_update(self):
        node = Node.objects.create(name='mynode', normal_data='{"test_attr": "foo"}')
        node.run_list.create(type='recipe', name='apt')
        chef_node = chef.Node('mynode')
        chef_node['test_attr'] = 'bar'
        chef_node.run_list = ['role[web_server]']
        chef_node.save()
        node = Node.objects.get(name='mynode')
        self.assertEqual(node.normal, {u'test_attr': u'bar'})
        self.assertEqual(node.run_list.count(), 1)
        self.assertEqual(node.run_list.all()[0].type, 'role')
        self.assertEqual(node.run_list.all()[0].name, 'web_server')

    def test_delete(self):
        Node.objects.create(name='mynode')
        chef.Node('mynode').delete()
        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(name='mynode')

    def test_cookbooks(self):
        node = Node.objects.create(name='mynode')
        node.run_list.create(type='recipe', name='apt')
        data = chef.Node('mynode').cookbooks()
        self.assertIn('apt', data)

    def test_cookbooks2(self):
        node = Node.objects.create(name='mynode')
        node.run_list.create(type='recipe', name='apache2')
        data = chef.Node('mynode').cookbooks()
        self.assertNotIn('apt', data)
