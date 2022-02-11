from .caching import get_yaml
import discord 

env = get_yaml("env.yaml")
DEAD_ROLE = env['dead-role']

def is_dead(player_object):
    if player_object is None:
        return None
    member_roles = [role.id for role in player_object.roles]
    if DEAD_ROLE in member_roles:
        return True
    else:
        return False

class WrongRoleError(Exception):
    """Raised if wrong role tries to use a command"""
    pass