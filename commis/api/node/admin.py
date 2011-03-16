import copy

from django.contrib import admin
from django.contrib.admin import helpers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from chef.rsa import SSLError

from commis.api.node.models import Node

class NodeAdmin(admin.ModelAdmin):
    fieldsets = [
        [None, {
            'fields': ['name']
        }],
    ]


admin.site.register(Node, NodeAdmin)
