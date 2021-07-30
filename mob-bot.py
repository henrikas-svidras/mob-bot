
import discord
from discord.ext import commands
import yaml

from mob_library.caching import get_yaml, smart_create_file, update_yaml_file
from mob_library.decorators import require

ENV_VARS = get_yaml("env.yaml")
TOKEN = ENV_VARS['bot-token']

### Create game state or use pre existing
GAME_STATE_FILE = ENV_VARS['game-state-file']
smart_create_file(GAME_STATE_FILE)
if get_yaml(GAME_STATE_FILE) is None:
    update_yaml_file(GAME_STATE_FILE, 'PRE_GAME', "game_state")

### Create vote tracking file or use pre existing
VOTE_TRACKING_FILE = ENV_VARS['vote-tracking-file']
smart_create_file(VOTE_TRACKING_FILE)
### Create vote tracking file or use pre existing
ALLIANCE_FILE = ENV_VARS['alliance-file']
smart_create_file(ALLIANCE_FILE)

### List of available roles
PLAYER_FILE = ENV_VARS['player-file']
smart_create_file(PLAYER_FILE)

AVAILABLE_ROLES = ENV_VARS['available-roles']

### Get admin role




### Discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='~!', intents=intents)

### Methods called through discord chat

# Commands to use before the game

@bot.command("register_player")
@commands.has_permissions(administrator=True)
@require(state="PRE_GAME")
async def register_player(ctx, player, role):
    smart_create_file(PLAYER_FILE)
    live_players = get_yaml(PLAYER_FILE)
    live_roles = []

    if not live_players is None:
        for p in live_players:
            print(f"Already assigned {p}.")
            live_roles.append(live_players[p]['role'])
    print(live_roles)
    discord_server = ctx.guild
    
    ### Tries to look up the targeted member:
    player_name = discord_server.get_member_named(player)
    # Checks if player name has been found
    if player_name is None:
        await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?")
    # Checks if such a role exists
    elif not role in AVAILABLE_ROLES:
        await ctx.channel.send(f"Cannot assign {player} the {role} because such a role is not defined as available!")
    # Checks if such a role has not yet been assigned
    elif role in live_roles:
        await ctx.channel.send(f"Cannot assign {player} the {role} because it is already assigned!")
    # Registers the player if all previous steps suceeded
    else:
        player_params = {
            "name": player_name.nick if not player_name.nick is None else player_name.name,
            "role": role,
            "state": "Alive",
        }
        live_roles.append(role)
        update_yaml_file(PLAYER_FILE, player_params, player_name.id)
        await ctx.channel.send(f"{player_name} is added, with the role {player_params['role']}.")
      
#@register_player.error
#async def register_player_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled if the game is started, available only in PRE_GAME.')

# Commands to start a round

@bot.command("begin_round")
@commands.has_permissions(administrator=True)
@require(state=["INTER_ROUND","PRE_GAME"])
async def begin_round(ctx):
    """The method to call when you want to begin a new round. It can only be called when you have your game in INTER_ROUND or PRE_GAME state.
    """
    
    data = get_yaml(GAME_STATE_FILE)
    # If round number has not yet been set, means this is the first round
    if not "Round" in data:
        new_round_number = 1
    else:
        new_round_number = int(data["Round"])+1

    players = get_yaml(PLAYER_FILE)
    update_yaml_file(VOTE_TRACKING_FILE, {p:p for p in players}, new_round_number)
    update_yaml_file(GAME_STATE_FILE, new_round_number, "Round")
    update_yaml_file(GAME_STATE_FILE, "IN_ROUND", "game_state")

    rounds_votes = {}
    
    await ctx.channel.send("Switching to IN_ROUND")
    await ctx.channel.send(f"We are in Round {new_round_number}")

#@begin_round.error
#async def begin_round_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled during IN_ROUND, because the round is already ongoing.')

# Commands to stop a round

@bot.command("stop_round")
@commands.has_permissions(administrator=True)
@require(state="IN_ROUND")
async def stop_round(ctx):
    update_yaml_file(GAME_STATE_FILE, "INTER_ROUND", "game_state")
    await ctx.channel.send("Switching IN_ROUND -> INTER_ROUND")

@stop_round.error
async def stop_round_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is already stopped.')

# Commands for players

@bot.command("vote")
@commands.has_role(ENV_VARS["alive-role"])
@require(state="IN_ROUND")
async def vote(ctx, player):

    discord_server = ctx.guild
    
    live_players = get_yaml(PLAYER_FILE)

    ### Tries to look up the targeted member:
    player_name = discord_server.get_member_named(player)
    if player_name.id in live_players:
        game_state = get_yaml(GAME_STATE_FILE)
        round_number = game_state['Round']
        votes = get_yaml(VOTE_TRACKING_FILE)
        round_votes = votes[round_number]
        round_votes[ctx.message.author.id] = player_name.id
        update_yaml_file(VOTE_TRACKING_FILE, round_votes, round_number)
        if not player_name is None:
            await ctx.channel.send(f"Your vote against {player_name} has been noted.")
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP with your vote.")
    else:
        await ctx.channel.send(f"You are trying to vote {player}, but such a player is not in the game!")

#@vote.error
#async def vote_error(ctx, error):
#    if isinstance(error, commands.DisabledCommand):
#        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is over.')

@bot.command("create_new_alliance")
@commands.has_role(ENV_VARS["alive-role"])
@require(state="IN_ROUND")
async def create_new_alliance(ctx, name):

    guild = ctx.guild
    member = ctx.author
    
    category = discord.utils.get(guild.categories, id=ENV_VARS['alliance-chats'])
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    await guild.create_text_channel(name, category=category, overwrites=overwrites)
    
    new_channel = discord.utils.get(category.channels, name=name, type=ChannelType.text)

    alliance = {
        'name': name,
        'state': 'unlocked',
        'members':[ctx.author.name],
    }
    
    update_yaml_file(ALLIANCE_FILE, alliance, new_channel.id)


@bot.command("add_player")
@commands.has_role(ENV_VARS["alive-role"])
@require(state="IN_ROUND")
async def add_player(ctx, player):

    guild = ctx.guild
    
    channel = ctx.channel
    
    alliances = get_yaml(ALLIANCE_FILE)

    if channel.id in alliances:
        alliance = alliances[channel.id]
        if alliance['state'] == 'unlocked':

            live_players = get_yaml(PLAYER_FILE)

            ### Tries to look up the targeted member:
            player_name = guild.get_member_named(player)
            if player_name is None:
                await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP.")
            elif player_name.id in live_players:
                await ctx.channel.send(f"{player_name} has been noted.")
            else:
                await ctx.channel.send(f"You are trying to add {player}, but such a player is not in the game!")
            
            alliance['members'].append(player_name.id)
            update_yaml_file(ALLIANCE_FILE, alliance, channel.id)

        else: # if alliance is locked
            return
    else: # if command called not in an alliance chat
        return


@bot.command("open_alliance")
@commands.has_role(ENV_VARS["alive-role"])
@require(state="IN_ROUND")
async def open_alliance(ctx):
    
    channel = ctx.channel
    
    alliances = get_yaml(ALLIANCE_FILE)

    if channel.id in alliances:
        alliance = alliances[channel.id]
        if alliance['state'] == 'unlocked':
            alliance['state'] = 'open'
            update_yaml_file(ALLIANCE_FILE, alliance, channel.id)
    
    # add everyone into alliance (TODO)

    

    



### Start bot
bot.run(TOKEN)
