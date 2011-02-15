from django.db import models

from django_extensions.db.fields import UUIDField, CreationDateTimeField

class Sandbox(models.Model):
    uuid = UUIDField()
    created = CreationDateTimeField()

class SandboxFile(models.Model):
    sandbox = models.ForeignKey(Sandbox, related_name='files')
    checksum = models.CharField(max_length=1024, unique=True)
    uploaded = models.BooleanField()
