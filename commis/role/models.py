import chef
from django.db import models

from commis.utils import json

class RoleManager(models.Manager):
    def from_dict(self, data):
        chef_role = chef.Role.from_search(data)
        role, created = self.get_or_create(name=chef_role.name)
        role.description = chef_role.description
        role.override_data = json.dumps(chef_role.override_attributes)
        role.default_data = json.dumps(chef_role.default_attributes)
        role.save()
        role.run_list.all().delete()
        for entry in chef_role.run_list:
            if '[' not in entry:
                continue # Can't parse this
            type, name = entry.split('[', 1)
            name = name.rstrip(']')
            role.run_list.create(type=type, name=name)
        return role


class Role(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    description = models.TextField()
    override_data = models.TextField()
    default_data = models.TextField()

    objects = RoleManager()

    def __unicode__(self):
        return self.name

    @property
    def override(self):
        if not self.override_data:
            return {}
        return json.loads(self.override_data)

    @property
    def default(self):
        if not self.default_data:
            return {}
        return json.loads(self.default_data)

    def to_dict(self):
        chef_role = chef.Role(self.name, skip_load=True)
        chef_role.description = self.description
        chef_role.run_list = [unicode(entry) for entry in self.run_list.all()]
        chef_role.default_attributes = self.default
        chef_role.override_attributes = self.override
        return chef_role

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


class RoleRunListEntry(models.Model):
    role = models.ForeignKey(Role, related_name='run_list')
    name = models.CharField(max_length=1024)
    type = models.CharField(max_length=1024, choices=[('recipe', 'Recipe'), ('role', 'Role')])

    def __unicode__(self):
        return u'%s[%s]'%(self.type, self.name)
