from chef.rsa import Key
from django.db import models

from commis.db import update

class ClientManager(models.Manager):
    def create(self, *args, **kwargs):
        client = super(ClientManager, self).create(*args, **kwargs)
        client.generate_key()
        return client


class Client(models.Model):
    name = models.CharField(unique=True, max_length=1024)
    key_pem = models.TextField()
    admin = models.BooleanField()

    objects = ClientManager()

    @property
    def key(self):
        if not self.key_pem:
            return None
        if not getattr(self, '_key_cache', None):
            self._key_cache = Key(self.key_pem)
        return self._key_cache

    def generate_key(self):
        key = Key.generate(2048)
        update(self, key_pem=key.public_export())
        self._key_cache = key
        return key
