
import discord
from discord.ext import commands
import yaml

from mob_library.caching import get_yaml, smart_create_file, update_yaml_file
from mob_library.decorators import require_inround, require_interround

env_vars = get_yaml("env.yaml")
TOKEN = env_vars['bot-token']

### Create game state or use pre existing
game_state_file = env_vars['game-state-file']
smart_create_file(game_state_file)

### Create vote tracking file or use pre existing
vote_tracking_file = env_vars['vote-tracking-file']
smart_create_file(vote_tracking_file)

### Discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='~!', intents=intents)

### Methods called through discord chat
@bot.command("begin_round")
@require_interround
async def begin_round(ctx):
    """The method to call when you want to begin a new round. It can only be called when you have your game in INTER_ROUND or PRE_GAME state.
    """
    
    data = get_yaml(game_state_file)
    if not "Round" in data:
        new_round_number = 1
    else:
        new_round_number = int(data["Round"])+1
    update_yaml_file(game_state_file, new_round_number, "Round")

    update_yaml_file(game_state_file, "IN_ROUND", "game_state")
    await ctx.channel.send("Switching INTER_ROUND -> IN_ROUND")
    await ctx.channel.send(f"We are in Round {new_round_number}")

@begin_round.error
async def info_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during IN_ROUND, because the round is already ongoing.')

@bot.command("stop_round")
@require_inround
async def stop_round(ctx):
    update_yaml_file(game_state_file, "INTER_ROUND", "game_state")
    await ctx.channel.send("Switching IN_ROUND -> INTER_ROUND")

@stop_round.error
async def info_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is already stopped.')

@bot.command("vote")
@require_inround
async def vote(ctx, player):

    discord_server = ctx.guild
    
    ### Tries to look up the member:
    player_name = discord_server.get_member_named(player)
    if not player_name is None:
        await ctx.channel.send(f"This person is trying to vote {player_name}")
    else:
        await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP with your vote.")

@stop_round.error
async def info_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is already stopped.')
### Start bot
bot.run(TOKEN)