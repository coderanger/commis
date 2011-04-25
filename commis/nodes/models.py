import chef
from django.core.urlresolvers import reverse
from django.db import models

from commis.roles.models import Role
from commis.utils import json
from commis.utils.dict import deep_merge

class NodeManager(models.Manager):
    def from_dict(self, data):
        chef_node = chef.Node.from_search(data)
        node, created = self.get_or_create(name=chef_node.name)
        node.automatic_data = json.dumps(chef_node.automatic)
        node.override_data = json.dumps(chef_node.override)
        node.normal_data = json.dumps(chef_node.normal)
        node.default_data = json.dumps(chef_node.default)
        node.save()
        node.run_list.all().delete()
        for entry in chef_node.run_list:
            if '[' not in entry:
                continue # Can't parse this
            type, name = entry.split('[', 1)
            name = name.rstrip(']')
            node.run_list.create(type=type, name=name)
        return node


class Node(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    automatic_data = models.TextField()
    override_data = models.TextField()
    normal_data = models.TextField()
    default_data = models.TextField()

    objects = NodeManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('commis_webui_nodes_show', args=(self,))

    @property
    def automatic(self):
        if not self.automatic_data:
            return {}
        return json.loads(self.automatic_data)

    @property
    def override(self):
        if not self.override_data:
            return {}
        return json.loads(self.override_data)

    @property
    def normal(self):
        if not self.normal_data:
            return {}
        return json.loads(self.normal_data)

    @property
    def default(self):
        if not self.default_data:
            return {}
        return json.loads(self.default_data)

    def to_dict(self):
        chef_node = chef.Node(self.name, skip_load=True)
        chef_node.automatic = self.automatic
        chef_node.override = self.override
        chef_node.normal = self.normal
        chef_node.default = self.default
        chef_node.run_list = [unicode(entry) for entry in self.run_list.all()]
        return chef_node

    def to_search(self):
        data = deep_merge(self.automatic, self.override, self.normal, self.default)
        data['name'] = self.name
        data['chef_type'] = 'node'
        run_list = list(self.run_list.all().order_by('id'))
        data['recipe'] = [entry.name for entry in run_list if entry.type == 'recipe']
        data['role'] = [entry.name for entry in run_list if entry.type == 'role']
        data['run_list'] = [entry.name for entry in run_list]
        return data

    def expand_run_list(self):
        recipes = []
        for entry in self.run_list.all().order_by('id'):
            if entry.type == 'role':
                try:
                    role = Role.objects.get(name=entry.name)
                except Role.DoesNotExist:
                    continue
                for recipe in role.expand_run_list():
                    if recipe not in recipes:
                        recipes.append(recipe)
            elif entry.type == 'recipe':
                if entry.name not in recipes:
                    recipes.append(entry.name)
        return recipes


class NodeRunListEntry(models.Model):
    node = models.ForeignKey(Node, related_name='run_list')
    name = models.CharField(max_length=1024)
    type = models.CharField(max_length=1024, choices=[('recipe', 'Recipe'), ('role', 'Role')])

    def __unicode__(self):
        return u'%s[%s]'%(self.type, self.name)
