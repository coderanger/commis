import chef

from commis.test import ChefTestCase
from commis.data_bags.models import DataBag, DataBagItem
from commis.utils import json

class DataBagAPITestCase(ChefTestCase):
    def test_list(self):
        DataBag.objects.create(name='mybag')
        self.assertIn('mybag', chef.DataBag.list())

    def test_create(self):
        chef.DataBag.create('mybag')
        DataBag.objects.get(name='mybag')

    def test_get(self):
        bag = DataBag.objects.create(name='mybag')
        bag.items.create(name='item1', data='{"id":"item1"}')
        bag.items.create(name='item2', data='{"id":"item2"}')
        self.assertEqual(len(chef.DataBag('mybag')), 2)
        self.assertIn('item1', chef.DataBag('mybag'))
        self.assertIn('item2', chef.DataBag('mybag'))

    def test_delete(self):
        DataBag.objects.create(name='mybag')
        chef.DataBag('mybag').delete()
        with self.assertRaises(DataBag.DoesNotExist):
            DataBag.objects.get(name='mybag')


class DataBagItemAPITestCase(ChefTestCase):
    def test_create(self):
        DataBag.objects.create(name='mybag')
        chef.DataBagItem.create('mybag', 'item1', attr=1)
        chef.DataBagItem.create('mybag', 'item2', attr=2)
        bag = DataBag.objects.get(name='mybag')
        self.assertEqual(bag.items.count(), 2)
        item = bag.items.get(name='item1')
        self.assertEqual(json.loads(item.data), {'id': 'item1', 'attr': 1})
        item = bag.items.get(name='item2')
        self.assertEqual(json.loads(item.data), {'id': 'item2', 'attr': 2})

    def test_get(self):
        bag = DataBag.objects.create(name='mybag')
        data = {'id': 'myitem', 'attr': 1, 'nested': {'nested_attr': 'foo'}}
        bag.items.create(name='myitem', data=json.dumps(data))
        chef_item = chef.DataBagItem('mybag', 'myitem')
        self.assertEqual(data, chef_item)

    def test_update(self):
        bag = DataBag.objects.create(name='mybag')
        data = {'id': 'myitem', 'attr': 1, 'nested': {'nested_attr': 'foo'}}
        bag.items.create(name='myitem', data=json.dumps(data))
        chef_item = chef.DataBagItem('mybag', 'myitem')
        chef_item['attr'] = 2
        chef_item['nested']['nested_attr'] = 'bar'
        chef_item.save()
        data2 = {'id': 'myitem', 'attr': 2, 'nested': {'nested_attr': 'bar'}}
        item = DataBagItem.objects.get(bag__name='mybag', name='myitem')
        self.assertEqual(json.loads(item.data), data2)

    def test_delete(self):
        bag = DataBag.objects.create(name='mybag')
        bag.items.create(name='myitem', data='{"id":"myitem"}')
        chef.DataBagItem('mybag', 'myitem').delete()
        with self.assertRaises(DataBagItem.DoesNotExist):
            DataBagItem.objects.get(bag__name='mybag', name='myitem')
