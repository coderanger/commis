from __future__ import absolute_import
from copy import copy

from django import template

from commis.api.role.models import Role
from commis.api.cookbook.models import CookbookRecipe

register = template.Library()

@register.inclusion_tag('commis/node/_form.html', takes_context=True)
def commis_node_form(context, node, form_info):
    data = copy(form_info)
    data['node'] = node
    data['available_roles'] = Role.objects.all()
    data['available_recipes'] = CookbookRecipe.objects.all()
    return data
