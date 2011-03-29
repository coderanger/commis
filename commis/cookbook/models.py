from django.core.urlresolvers import reverse
from django.db import models

from commis.exceptions import ChefAPIError
from commis.sandbox.models import SandboxFile

class CookbookManager(models.Manager):
    def from_dict(self, data):
        cookbook, created = self.get_or_create(name=data['cookbook_name'], version=data['version'])
        if 'metadata' in data:
            cookbook.maintainer = data['metadata'].get('maintainer', '')
            cookbook.maintainer_email = data['metadata'].get('maintainer_email', '')
            cookbook.description = data['metadata'].get('description', '')
            cookbook.long_description = data['metadata'].get('long_description', '')
            cookbook.license = data['metadata'].get('license', '')
        dependencies = data.get('metadata', {}).get('dependencies', {})
        for dep in cookbook.dependencies.all():
            if dep.name not in dependencies:
                # Dependency removed
                dep.delete()
        # I don't know what the value here is exactly. It is likely the dependency version in some form
        for name, _unknown in dependencies.iteritems():
            cookbook.dependencies.get_or_create(name=name)
        recipes = data.get('metadata', {}).get('recipes', {})
        for recipe in cookbook.recipes.all():
            if recipe.name not in recipes:
                recipe.delete()
        for name, description in recipes.iteritems():
            try:
                recipe = cookbook.recipes.get(name=name)
                recipe.description = description
                recipe.save()
            except CookbookRecipe.DoesNotExist:
                cookbook.recipes.create(name=name, description=description)
        for type, label in CookbookFile.TYPES:
            for file_info in data.get(type, []):
                try:
                    cookbook_file = cookbook.files.get(type=type, file__checksum=file_info['checksum'])
                except CookbookFile.DoesNotExist:
                    try:
                        file = SandboxFile.objects.get(checksum=file_info['checksum'])
                    except SandboxFile.DoesNotExist:
                        raise ChefAPIError(500, 'Checksum %s does not match any uploaded file', file_info['checksum'])
                    if not file.uploaded:
                        raise ChefAPIError(500, 'Checksum %s does not match any uploaded file', file_info['checksum'])
                    cookbook_file = cookbook.files.create(type=type, file=file)
                cookbook_file.name = file_info['name']
                cookbook_file.path = file_info['path']
                cookbook_file.specificity = file_info['specificity']
                cookbook_file.save()
        cookbook.save()
        return cookbook


class Cookbook(models.Model):
    name = models.CharField(max_length=1024)
    version = models.CharField(max_length=1024)
    maintainer = models.CharField(max_length=1024, blank=True)
    maintainer_email = models.CharField(max_length=1024, blank=True)
    description = models.CharField(max_length=1024, blank=True)
    long_description = models.TextField(blank=True)
    license = models.CharField(max_length=1024, blank=True)

    objects = CookbookManager()

    def to_dict(self, request=None):
        data = {}
        data['name'] = self.name + '-' + self.version
        data['cookbook_name'] = self.name
        data['version'] = self.version
        data['json_class'] = 'Chef::CookbookVersion'
        data['chef_type'] = 'cookbook_version'
        metadata = data['metadata'] = {}
        metadata['name'] = self.name
        metadata['version'] = self.version
        metadata['maintainer'] = self.maintainer
        metadata['maintainer_email'] = self.maintainer_email
        metadata['description'] = self.description
        metadata['long_description'] = self.long_description
        metadata['license'] = self.license
        dependencies = metadata['dependencies'] = {}
        for dep in self.dependencies.all():
            dependencies[dep.name] = []
        recipes = metadata['recipes'] = {}
        for recipe in self.recipes.all():
            recipes[recipe.name] = recipe.description
        # Not storing this info for now, fill in later with real code
        metadata['attributes'] = {}
        metadata['suggestions'] = {}
        metadata['platforms'] = {}
        metadata['recommendations'] = {}
        metadata['conflicting'] = {}
        metadata['groupings'] = {}
        metadata['replacing'] = {}
        metadata['providing'] = {}
        for type, label in CookbookFile.TYPES:
            data[type] = []
        for file in self.files.all():
            data[file.type].append(file.to_dict(request))
        return data


class CookbookFile(models.Model):
    TYPES = (
        ('definitions', 'Definition'),
        ('attributes', 'Attribute'),
        ('files', 'File'),
        ('libraries', 'Library'),
        ('templates', 'Template'),
        ('providers', 'Provider'),
        ('resources', 'Resource'),
        ('recipes', 'Recipe'),
        ('root_files', 'Root File'),
    )
    cookbook = models.ForeignKey(Cookbook, related_name='files')
    type = models.CharField(max_length=32, choices=TYPES)
    name = models.CharField(max_length=1024)
    file = models.ForeignKey(SandboxFile, related_name='cookbook_files')
    path = models.CharField(max_length=1024)
    specificity = models.CharField(max_length=1024)

    def to_dict(self, request=None):
        data = {
            'name': self.name,
            'checksum': self.file.checksum,
            'path': self.path,
            'specificity': self.specificity,
        }
        if request:
            data['url'] = request.build_absolute_uri(reverse('cookbook_file', args=[self.cookbook.name, self.cookbook.version, self.file.checksum]))
        return data


class CookbookDependency(models.Model):
    cookbook = models.ForeignKey(Cookbook, related_name='dependencies')
    name = models.CharField(max_length=1024)


class CookbookRecipe(models.Model):
    cookbook = models.ForeignKey(Cookbook, related_name='recipes')
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name
