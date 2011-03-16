import chef
from chef.rsa import Key
from django.db import models
from django.utils.translation import ugettext as _

from commis.api import conf
from commis.db import update

class ClientManager(models.Manager):
    def create(self, *args, **kwargs):
        client = super(ClientManager, self).create(*args, **kwargs)
        client.generate_key()
        return client


class Client(models.Model):
    name = models.CharField(_('Name'), unique=True, max_length=1024)
    key_pem = models.TextField(_('Public Key'))
    admin = models.BooleanField(_('Admin'))

    objects = ClientManager()

    def __unicode__(self):
        return self.name

    @property
    def key(self):
        if not self.key_pem:
            return None
        if not getattr(self, '_key_cache', None):
            self._key_cache = Key(self.key_pem)
        return self._key_cache

    @property
    def validator(self):
        return self.name == conf.COMMIS_VALIDATOR_NAME

    def generate_key(self):
        key = Key.generate(2048)
        update(self, key_pem=key.public_export())
        self._key_cache = key
        return key

    def to_dict(self):
        client = chef.Client(self.name, skip_load=True)
        client.admin = self.admin
        client.public_key = self.key_pem
        return client.to_dict()
