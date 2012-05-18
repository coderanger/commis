import chef
from chef.rsa import Key
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from commis import conf
from commis.db import update

class ClientManager(models.Manager):
    def create(self, *args, **kwargs):
        client = super(ClientManager, self).create(*args, **kwargs)
        client.generate_key()
        return client

    def from_dict(self, data, *args, **kwargs):
        chef_client = chef.Client.from_search(data)
        client, created = self.get_or_create(name=chef_client.name)
        client.generate_key()
        client.save()
        client.private_key = client._key_cache.private_export()
        return client

class Client(models.Model):
    name = models.CharField(_('Name'), unique=True, max_length=1024)
    key_pem = models.TextField(_('Public Key'))
    admin = models.BooleanField(_('Admin'))

    objects = ClientManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('commis_webui_clients_show', args=(self,))

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

    def to_search(self):
        return self.to_dict()
