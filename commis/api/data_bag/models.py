import os

import chef
from django.conf import settings
from django.db import models

from commis.api import conf
from commis.api.models import Client
from commis.db import update
from commis.utils import json
from commis.utils.dict import deep_merge

class DataBag(models.Model):
    name = models.CharField(max_length=1024, unique=True)

    def to_dict(self):
        chef_node = chef.Node(self.name, skip_load=True)
        chef_node.automatic = self.automatic
        chef_node.override = self.override
        chef_node.normal = self.normal
        chef_node.default = self.default
        chef_node.run_list = [unicode(entry) for entry in self.run_list.all()]
        return chef_node


class DataBagItem(models.Model):
    bag = models.ForeignKey(DataBag, related_name='items')
    name = models.CharField(max_length=1024)
    data = models.TextField()

    def to_search(self):
        return json.loads(self.data)
