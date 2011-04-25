from haystack import site

from commis.roles.models import Role
from commis.search.indexes import CommisSearchIndex

class RoleIndex(CommisSearchIndex):
    pass

site.register(Role, RoleIndex)
