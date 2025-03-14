from django import template
from league.models import Team

register = template.Library()

@register.filter
def is_user_team(team):
 
    return isinstance(team, Team)
