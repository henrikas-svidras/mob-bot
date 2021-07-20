
import discord
from discord.ext import commands
import yaml

from mob_library.caching import get_yaml, smart_create_file, update_yaml_file
from mob_library.decorators import require_inround, require_interround, require_pregame

env_vars = get_yaml("env.yaml")
TOKEN = env_vars['bot-token']

### Create game state or use pre existing
game_state_file = env_vars['game-state-file']
smart_create_file(game_state_file)

### Create vote tracking file or use pre existing
vote_tracking_file = env_vars['vote-tracking-file']
smart_create_file(vote_tracking_file)

### List of available roles
player_file = env_vars['player-file']
available_roles = env_vars['available_roles']
print(available_roles)

### Discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='~!', intents=intents)

### Methods called through discord chat

# Commands to use before the game

@bot.command("register_player")
@require_pregame
async def register_player(ctx, player, role):
    smart_create_file(player_file)
    live_players = get_yaml(player_file)
    live_roles = []

    if not live_players is None:
        for p in live_players:
            print(f"Already assigned {p}.")
            live_roles.append(live_players[p])

    discord_server = ctx.guild
    
    print(discord_server)
    ### Tries to look up the targeted member:
    player_name = discord_server.get_member_named(player)
    # Checks if player name has been found
    if player_name is None:
        await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?")
    # Checks if such a role exists
    elif not role in available_roles:
        await ctx.channel.send(f"Cannot assign {player} the {role} because such a role is not defined as available!")
    # Checks if such a role has not yet been assigned
    elif role in live_roles:
        await ctx.channel.send(f"Cannot assign {player} the {role} because it is already assigned!")
    # Registers the player if all previous steps suceeded
    else:
        update_yaml_file(player_file, role, player_name.id)
        await ctx.channel.send(f"{player_name} is added, with the role {role}.")
      
#@register_player.error
#async def register_player_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled if the game is started, available only in PRE_GAME.')

# Commands to start a round

@bot.command("begin_round")
@require_interround
async def begin_round(ctx):
    """The method to call when you want to begin a new round. It can only be called when you have your game in INTER_ROUND or PRE_GAME state.
    """
    
    data = get_yaml(game_state_file)
    # If round number has not yet been set, means this is the first round
    if not "Round" in data:
        new_round_number = 1
    else:
        new_round_number = int(data["Round"])+1

    players = get_yaml(player_file)
    update_yaml_file(vote_tracking_file, {p:p for p in players}, new_round_number)
    update_yaml_file(game_state_file, new_round_number, "Round")
    update_yaml_file(game_state_file, "IN_ROUND", "game_state")

    rounds_votes = {}
    
    await ctx.channel.send("Switching INTER_ROUND -> IN_ROUND")
    await ctx.channel.send(f"We are in Round {new_round_number}")

#@begin_round.error
#async def begin_round_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled during IN_ROUND, because the round is already ongoing.')

# Commands to stop a round

@bot.command("stop_round")
@require_inround
async def stop_round(ctx):
    update_yaml_file(game_state_file, "INTER_ROUND", "game_state")
    await ctx.channel.send("Switching IN_ROUND -> INTER_ROUND")

@stop_round.error
async def stop_round_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is already stopped.')

# Commands for players

@bot.command("vote")
@require_inround
async def vote(ctx, player):

    discord_server = ctx.guild
    
    live_players = get_yaml(player_file)

    ### Tries to look up the targeted member:
    player_name = discord_server.get_member_named(player)
    if player_name.id in live_players:
        game_state = get_yaml(game_state_file)
        round_number = game_state['Round']
        votes = get_yaml(vote_tracking_file)
        round_votes = votes[round_number]
        round_votes[ctx.message.author.id] = player_name.id
        update_yaml_file(vote_tracking_file, round_votes, round_number)
        if not player_name is None:
            await ctx.channel.send(f"This person is trying to vote {player_name}")
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP with your vote.")
    else:
        await ctx.channel.send(f"You are trying to vote {player}, but such a player is not in the game!")

#@vote.error
#async def vote_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is over.')

### Start bot
bot.run(TOKEN)