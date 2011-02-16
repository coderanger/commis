import os

from django.conf import settings
from django.db import models
from django_extensions.db.fields import UUIDField, CreationDateTimeField

from commis.api import conf
from commis.api.models import Client
from commis.db import update

class Sandbox(models.Model):
    uuid = UUIDField()
    created = CreationDateTimeField()

    def commit(self):
        completed = []
        for sandbox_file in self.files.all():
            try:
                sandbox_file.commit()
            except Exception, e:
                # Undo and bail
                self.uncommit(completed)
                raise

    def uncommit(self, completed):
        for sandbox_file in completed:
            try:
                sandbox_file.uncommit()
            except Exception, e:
                pass


class SandboxFile(models.Model):
    sandbox = models.ForeignKey(Sandbox, related_name='files')
    checksum = models.CharField(max_length=1024, unique=True)
    uploaded = models.BooleanField()
    content_type = models.CharField(max_length=32)
    created_by = models.ForeignKey(Client, related_name='+')

    @property
    def path(self):
        if self.uploaded:
            return self.commit_path
        else:
            return self.pending_path

    @property
    def commit_path(self):
        return os.path.join(conf.COMMIS_FILE_ROOT, self.checksum[0], self.checksum[1], self.checksum)

    @property
    def pending_path(self):
        return os.path.join(conf.COMMIS_FILE_ROOT, 'pending', self.sandbox.uuid, self.checksum[0], self.checksum[1], self.checksum)

    def write(self, data):
        path = self.pending_path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        open(path, 'wb').write(data)

    def commit(self):
        path = self.commit_path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if os.path.exists(path):
            raise SandboxConflict
        rows = SandboxFile.objects.filter(id=self.id, uploaded=False).update(uploaded=True)
        if not rows:
            raise SandboxConflict
        self.uploaded = True
        os.rename(self.pending_path, path)

    def uncommit(self):
        path = self.pending_path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if os.path.exists(path):
            os.unlink(path)
        rows = SandboxFile.objects.filter(id=self.id, uploaded=True).update(uploaded=False)
        if not rows:
            raise SandboxConflict
        self.uploaded = False
        os.rename(self.commit_path, path)
