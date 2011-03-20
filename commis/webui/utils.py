from django.contrib.admin import util
from django.db import router

class FakeAdminSite(object):
    def __init__(self):
        self._registry = ()
fake_admin_site = FakeAdminSite()


def get_deleted_objects(obj, request):
    opts = obj._meta
    using = router.db_for_write(obj)
    return util.get_deleted_objects([obj], opts, request.user, fake_admin_site, using)
