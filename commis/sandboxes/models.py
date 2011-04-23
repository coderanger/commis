import os

from django.db import models
from django_extensions.db.fields import UUIDField, CreationDateTimeField

from commis import conf
from commis.clients.models import Client
from commis.sandboxes.exceptions import SandboxConflict

class Sandbox(models.Model):
    uuid = UUIDField()
    created = CreationDateTimeField()

    def commit(self):
        completed = []
        for sandbox_file in self.files.all():
            try:
                sandbox_file.commit(self)
            except Exception:
                # Undo and bail
                self.uncommit(completed)
                raise
        self.delete()

    def uncommit(self, completed):
        for sandbox_file in completed:
            try:
                sandbox_file.uncommit(self)
            except Exception:
                pass


class SandboxFile(models.Model):
    sandboxes = models.ManyToManyField(Sandbox, related_name='files')
    checksum = models.CharField(max_length=1024, unique=True)
    uploaded = models.BooleanField()
    content_type = models.CharField(max_length=32)
    created_by = models.ForeignKey(Client, related_name='+')

    @property
    def path(self):
        return os.path.join(conf.COMMIS_FILE_ROOT, self.checksum[0], self.checksum[1], self.checksum)

    @property
    def content(self):
        if not self.uploaded:
            raise ValueError('File not uploaded')
        return open(self.path, 'rb').read()

    def pending_path(self, sandbox):
        return os.path.join(conf.COMMIS_FILE_ROOT, 'pending', sandbox.uuid, self.checksum[0], self.checksum[1], self.checksum)

    def write(self, sandbox, data):
        path = self.pending_path(sandbox)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        open(path, 'wb').write(data)

    def commit(self, sandbox):
        path = self.path
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if os.path.exists(path):
            raise SandboxConflict
        rows = SandboxFile.objects.filter(id=self.id, uploaded=False).update(uploaded=True)
        if not rows:
            raise SandboxConflict
        self.uploaded = True
        self.sandboxes.remove(sandbox)
        os.rename(self.pending_path(sandbox), path)

    def uncommit(self, sandbox):
        path = self.pending_path(sandbox)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if os.path.exists(path):
            os.unlink(path)
        rows = SandboxFile.objects.filter(id=self.id, uploaded=True).update(uploaded=False)
        if not rows:
            raise SandboxConflict
        self.uploaded = False
        self.sandboxes.add(sandbox)
        try:
            os.rename(self.path, path)
        except Exception:
            os.unlink(self.path)
