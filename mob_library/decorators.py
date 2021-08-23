import functools
from .caching import get_yaml
from discord.ext.commands import DisabledCommand

def require(state=None):
    def decorator(func):
        """A decorator instance
        """
        @functools.wraps(func)
        async def wrapper_func(*args, **kwargs):

            # Checks game state

            if not state is None:

                env = get_yaml('env.yaml')
                game_state_file = get_yaml(env['game-state-file'])
                game_state = game_state_file["game_state"]
                if (isinstance(state, str) and not game_state == state) or (isinstance(state, list) and not game_state in state):
                    raise DisabledCommand(
                        f"Game is currently not in {game_state} state, meaning this command cannot be called.")
            
            # Checks role (TODO)
            # Checks channel (TODO)

            return await func(*args, **kwargs)
        return wrapper_func
    return decorator
