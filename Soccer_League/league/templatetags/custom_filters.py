from django import template
from league.models import Team

register = template.Library()

@register.filter
def is_user_team(team):

    return isinstance(team, Team)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])
