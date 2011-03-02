import os

import chef

from commis.api import conf
from commis.api.tests import ChefTestCase
from commis.api.data_bag.models import DataBag
from commis.utils import json

class SearchAPITestCase(ChefTestCase):
    def test_bag(self):
        bag = DataBag.objects.create(name='mybag')
        data = {'id': 'item1', 'attr': 1, 'nested': {'nested_attr': 'foo'}}
        bag.items.create(name='item1', data=json.dumps(data))
        data = {'id': 'item2', 'attr': 1, 'nested': {'nested_attr': 'bar'}}
        bag.items.create(name='item2', data=json.dumps(data))
        data = {'id': 'item3', 'attr2': 1}
        bag.items.create(name='item3', data=json.dumps(data))
        chef_query = chef.Search('mybag', 'attr:1')
        self.assertEqual(len(chef_query), 2)
        self.assertIn('item1', chef_query)
        self.assertIn('item2', chef_query)
