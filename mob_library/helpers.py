from .caching import get_yaml

env = get_yaml("env.yaml")
DEAD_ROLE = env['dead-role']

def is_dead(player):
    member_object = discord.utils.get(guild.members, id=player)
    if member_object is None:
        return None
    member_roles = [role.name for role in member_object.roles]
    if DEAD_ROLE in member_roles:
        return True
    else:
        return False
