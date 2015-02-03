from django import template
from blog.utils import has_enough_privileges


register = template.Library()


@register.filter(name='has_permission_level')
def has_permission_level(user, group_name):
    return has_enough_privileges(user.role, group_name)
