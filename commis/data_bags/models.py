import chef
from django.db import models

from commis.utils import json

class DataBagManager(models.Manager):
    def from_dict(self, data):
        return self.get_or_create(name=data['name'])[0]


class DataBag(models.Model):
    name = models.CharField(max_length=1024, unique=True)

    objects = DataBagManager()

    def __unicode__(self):
        return self.name

    def to_dict(self):
        chef_bag = chef.DataBag(self.name, skip_load=True)
        return chef_bag


class DataBagItem(models.Model):
    bag = models.ForeignKey(DataBag, related_name='items')
    name = models.CharField(max_length=1024)
    data = models.TextField()

    def __unicode__(self):
        return self.name

    @property
    def object(self):
        if self.data:
            return json.loads(self.data)
        return {}

    def to_search(self):
        data = self.object
        data['chef_type'] = 'data_bag_item'
        data['data_bag'] = self.bag.name
        return data

    def to_dict(self):
        return {
            'name': 'data_bag_item_%s_%s'%(self.bag.name, self.name),
            'data_bag': self.bag.name,
            'json_class': 'Chef::DataBagItem',
            'chef_type': 'data_bag_item',
            'raw_data': json.loads(self.data),
        }