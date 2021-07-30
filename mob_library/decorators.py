import functools
from .caching import get_yaml
from discord.ext.commands import DisabledCommand

# def require_interround(func):
#     """A decorator instance requiring that current game_state is set to INTER_ROUND
#     """
#     @functools.wraps(func)
#     async def wrapper_func(*args, **kwargs):
#         env = get_yaml('env.yaml')
#         game_state_file = get_yaml(env['game-state-file'])
#         game_state = game_state_file["game_state"]
#         if not game_state == "INTER_ROUND":
#             raise DisabledCommand("Game is currently not in INTER_ROUND state, meaning this command cannot be called.")
#         return await func(*args, **kwargs)
#     return wrapper_func

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

# def require_inround(func):
#     """A decorator instance requiring that current game_state is set to IN_ROUND
#     """
#     @functools.wraps(func)
#     async def wrapper_func(*args, **kwargs):
#         env = get_yaml('env.yaml')
#         game_state_file = get_yaml(env['game-state-file'])
#         game_state = game_state_file["game_state"]
#         if not game_state == "IN_ROUND":
#             raise DisabledCommand("Game is currently not in IN_ROUND state, meaning this command cannot be called.")
#         return await func(*args, **kwargs)
#     return wrapper_func

# def require_pregame(func):
#     """A decorator instance requiring that current game_state is set to PRE_GAME
#     """
#     @functools.wraps(func)
#     async def wrapper_func(*args, **kwargs):
#         env = get_yaml('env.yaml')
#         game_state_file = get_yaml(env['game-state-file'])
#         game_state = game_state_file["game_state"]
#         if not game_state == "PRE_GAME":
#             raise DisabledCommand("Game is currently not in PRE_GAME state, meaning this command cannot be called.")
#         return await func(*args, **kwargs)
#     return wrapper_func
