
from mob_library.helpers import is_dead
import discord
from discord.ext import commands
import yaml

import time 

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

### Create item tracking file or use pre existing
ITEM_TRACKING_FILE = ENV_VARS['item-tracking-file']
smart_create_file(ITEM_TRACKING_FILE)

### Create alliance tracking file or use pre existing
ALLIANCE_FILE = ENV_VARS['alliance-file']
smart_create_file(ALLIANCE_FILE)

### List of available roles
PLAYER_FILE = ENV_VARS['player-file']
smart_create_file(PLAYER_FILE)

AVAILABLE_ROLES = ENV_VARS['available-roles']


# Miscalenous
def check_if_confessional(ctx):
    return ctx.channel.category.id == ENV_VARS['confessional-chats']

def check_if_purgatory(ctx):
    return ctx.channel.id == ENV_VARS['purgatory-channel']

def check_if_host_chats(ctx):
    return ctx.channel.id == ENV_VARS['host-chats']

### Discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='^', intents=intents)

### Methods called through discord chat

# Commands to use before the game

@bot.command("register_player", hidden=True)
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

    discord_server = ctx.guild
    
    ### Tries to look up the targeted member:
    player_object = discord_server.get_member_named(player)
    # Checks if player name has been found
    if player_object is None:
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
            "name": player_object.nick if not player_object.nick is None else player_object.name,
            "role": role,
            "uses": 0,
            "state": "Alive",
            "inventory": [],
            "confessional-id":0,
            "submission-id":0
        }
        live_roles.append(role)
        update_yaml_file(PLAYER_FILE, player_params, player_object.id)
        alive_role = discord.utils.get(discord_server.roles, id=ENV_VARS['alive-role'])
        await player_object.add_roles(alive_role) #adds the role
        await ctx.channel.send(f"{player_params['name']} is added, with the role {player_params['role']}.")
      
@register_player.error
async def register_player_error(ctx, error):
   if isinstance(error, commands.DisabledCommand):
       await ctx.channel.send('This command is disabled if the game is started, available only in PRE_GAME.')

# Commands to start a round

@bot.command("begin_round", hidden=True)
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
    update_yaml_file(ITEM_TRACKING_FILE, {p:p for p in players}, new_round_number)
    update_yaml_file(GAME_STATE_FILE, new_round_number, "Round")
    update_yaml_file(GAME_STATE_FILE, "IN_ROUND", "game_state")

    rounds_votes = {}
    
    await ctx.channel.send("Switching to IN_ROUND")
    await ctx.channel.send(f"We are in Round {new_round_number}")

@begin_round.error
async def begin_round_error(ctx, error):
   if isinstance(error, commands.DisabledCommand):
       await ctx.channel.send('This command is disabled during IN_ROUND, because the round is already ongoing.')

# Commands to stop a round

@bot.command("stop_round", hidden=True)
@commands.has_permissions(administrator=True)
@require(state="IN_ROUND")
async def stop_round(ctx):
    update_yaml_file(GAME_STATE_FILE, "INTER_ROUND", "game_state")
    await ctx.channel.send("Switching IN_ROUND -> INTER_ROUND")

@stop_round.error
async def stop_round_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.channel.send('This command is disabled during INTER_ROUND, because the round is already stopped.')

@bot.command("kill_player", hidden=True)
@commands.has_permissions(administrator=True)
@require(state="INTER_ROUND")
async def kill_player(ctx, player, is_jury=None):
    """A method to kill a player (set to dead). Takes as input player name, and whether to kill player (by default) or set to jury. 
    If the latter functionality is requested add "jury" to the command, e.g: ^kill_player EvilPlayer jury
    """
    discord_server = ctx.guild

    player_object = discord_server.get_member_named(player)
    live_players = get_yaml(PLAYER_FILE)
    alliances = get_yaml(ALLIANCE_FILE)

    if player_object is None:
        name_variants = get_yaml('name-variants.yaml')
        if player in name_variants:
            player_object = discord_server.get_member_named(name_variants[player])
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP.")
            return
    elif not player_object.id in live_players: 
        await ctx.channel.send(f"{player} is found in server but not playing!")
        return
    else:
        player = live_players[player_object.id]
        if player["state"] == "Alive":
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            if is_jury == 'Jury' or is_jury == 'jury':
                await ctx.channel.send(f"{display_name} will be killed (moved to 'Jury' role)")
            else:
                await ctx.channel.send(f"{display_name} will be killed (moved to 'Dead' role)")
            player["state"] = 'Dead'
            update_yaml_file(PLAYER_FILE, player, player_object.id)
            for alliance, stats in alliances.items():
                if player_object.id in stats['members']:
                    stats['members'].remove(player_object.id)

                    alliance_channel = discord.utils.get(discord_server.channels, id=alliance)

                    # overwrite = discord.PermissionOverwrite()
                    # overwrite.send_messages = False
                    # overwrite.read_messages = False

                    await alliance_channel.set_permissions(player_object, overwrite=None)
                    await alliance_channel.send(f"***{display_name} removed***")


                update_yaml_file(ALLIANCE_FILE, stats, alliance)
            await ctx.channel.send(f"Removed from alliances")
            alive_role = discord.utils.get(discord_server.roles, id=ENV_VARS['alive-role'])
            
            await player_object.remove_roles(alive_role) #adds the role
            if is_jury == 'Jury' or is_jury == 'jury':
                jury_role = discord.utils.get(discord_server.roles, id=ENV_VARS['jury-role'])
                await player_object.add_roles(jury_role) #adds the role
                await ctx.channel.send(f"Added Jury role")

            else:
                dead_role = discord.utils.get(discord_server.roles, id=ENV_VARS['dead-role'])
                await player_object.add_roles(dead_role) #adds the role
                await ctx.channel.send(f"Added Dead role")
        else:
            await ctx.channel.send(f"It seems that you are trying to kill an already dead player.")

@bot.command("send_all", hidden=True)
@commands.has_permissions(administrator=True)
async def send_all(ctx, message_id):
    """The command will resend a message that you have composed to everyone. 
    Send the message to any chat and give the message ID to this command.
    """
    
    discord_server = ctx.guild
    message = await ctx.fetch_message(message_id)
    live_players = get_yaml(PLAYER_FILE)

    if message is None:
        await ctx.channel.send(f"Didn't find the picture rip")
        return
    else:
        await ctx.channel.send(f"Found the message {message_id}")
    file_to_send = await message.attachments[0].to_file()

    await ctx.channel.send(f"Will now send it for all players")
 
    for player in live_players.values():
        if player['state'] == 'Alive':
            time.sleep(0.1) # TO avoid being treated as spamming and getting rate limited
            confessional_channel = discord.utils.get(discord_server.channels, id=player['confessional-id'])
            submission_channel = discord.utils.get(discord_server.channels, id=player['submission-id'])
            file_to_send = await message.attachments[0].to_file()

            msg = await confessional_channel.send(file=file_to_send)
            await msg.pin()
            file_to_send = await message.attachments[0].to_file()
            msg = await submission_channel.send(file=file_to_send)
            await msg.pin()
    
    await ctx.channel.send("Sent to all Alive players.")

@bot.command("find_player_nick", hidden=True)
@commands.has_permissions(administrator=True)
async def find_player_nick(ctx, player):
    discord_server = ctx.guild
    player_object = discord_server.get_member_named(player)
    if player_object is None:
        name_variants = get_yaml('name-variants.yaml')
        if player in name_variants:
            player_object = discord_server.get_member_named(name_variants[player])
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP.")
            return
    display_name = player_object.nick if not player_object.nick is None else player_object.name
    await ctx.channel.send(f"yo I found {display_name}")

@bot.command("announce", hidden=True)
@commands.has_permissions(administrator=True)
async def find_player_nick(ctx, message_id:int, channel_id:int=None):
    discord_server = ctx.guild
    if channel_id is None:
        channel = ctx.channel
    else:
        channel = discord.utils.get(discord_server.channels, id=channel_id)
    message = await ctx.fetch_message(message_id)

    await channel.send(message.content)


 
@bot.command("revive_player", hidden=True)
@commands.has_permissions(administrator=True)
@require(state="IN_ROUND")
async def revive_player(ctx, player):
    discord_server = ctx.guild

    player_object = discord_server.get_member_named(player)
    live_players = get_yaml(PLAYER_FILE)

    if player_object is None:
        name_variants = get_yaml('name-variants.yaml')
        if player in name_variants:
            player_object = discord_server.get_member_named(name_variants[player])
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP.")
            return
    elif not player_object.id in live_players: 
        await ctx.channel.send(f"{player} is found in server but not playing!")
        return
    else:
        player = live_players[player_object.id]
        if player["state"] == "Alive":
            display_name = player_object.nick if not player_object.nick is None else player_object.name

            await ctx.channel.send(f"{display_name} is alive, can't revive.")
        else:
            player["state"] = 'Alive'
            player["role"] = 'None'
            update_yaml_file(PLAYER_FILE, player, player_object.id)
            alive_role = discord.utils.get(discord_server.roles, id=ENV_VARS['alive-role'])
            dead_role = discord.utils.get(discord_server.roles, id=ENV_VARS['dead-role'])
            await player_object.remove_roles(dead_role) #adds the role
            await player_object.add_roles(alive_role) #adds the role

            submission_channel = discord.utils.get(discord_server.channels, id=player["submission-id"])
            await submission_channel.send(f"{player_object.mention} You have been reviven by the Necromancer!")

            display_name = player_object.nick if not player_object.nick is None else player_object.name

            await ctx.channel.send(f"{display_name} has been revived.")


@bot.command("print_vote", hidden=True)
@commands.check(check_if_host_chats)
@commands.has_permissions(administrator=True)
async def print_vote(ctx, round=None):
    discord_server = ctx.guild
    if round is None:
        round = get_yaml(GAME_STATE_FILE)['Round']

    votes = get_yaml(VOTE_TRACKING_FILE)
    players = get_yaml(PLAYER_FILE)
    message_dic = {}
    for voter, votee in votes[round].items(): 
        voter_object = discord_server.get_member(voter)
        votee_object = discord_server.get_member(votee)
        voter_name = voter_object.nick if not voter_object.nick is None else voter_object.name
        votee_name = votee_object.nick if not votee_object.nick is None else votee_object.name
        if players[voter_object.id]['state'] == 'Dead':
            continue
        elif players[voter_object.id]['role'] == 'Parasite':
            message_dic[f'{voter_name}'] = 'N/A\n'
        else:
            message_dic[f'{voter_name}'] = f'{votee_name}\n'
    
    message = ''
    for voter in sorted(message_dic):
        message += f'{voter}: {message_dic[voter]}'

    await ctx.channel.send(message)
    
# Commands for players

@bot.command("vote", hidden=False)
@commands.has_role(ENV_VARS["alive-role"])
@require(state="IN_ROUND")
async def vote(ctx, player):
    """A command to vote against another player
    Usage example:
        ^vote player1
    You do not need to @ the player. Simply put their nickname, as you see them in the server.
    """

    discord_server = ctx.guild
    
    players = get_yaml(PLAYER_FILE)

    ### Tries to look up the targeted member:
    player_object = discord_server.get_member_named(player)

    if player_object is None:
        name_variants = get_yaml('name-variants.yaml')
        if player in name_variants:
            player_object = discord_server.get_member_named(name_variants[player])
        else:
            await ctx.channel.send(f"Can't find '{player}'. Maybe you spelled the name incorrectly? That also includes case sensitivity. \nIf you are sure that is a correct call please ping @Host ASAP with your vote.")
            return

    if player_object.id in players:
        if players[player_object.id]['state'] == 'Alive':
            if players[ctx.author.id]['role'] == 'Parasite':
                await ctx.channel.send(f"The Parasite does not have a regular vote.")
            else:
                game_state = get_yaml(GAME_STATE_FILE)
                round_number = game_state['Round']
                votes = get_yaml(VOTE_TRACKING_FILE)
                round_votes = votes[round_number]
                round_votes[ctx.message.author.id] = player_object.id
                update_yaml_file(VOTE_TRACKING_FILE, round_votes, round_number)
                display_name = player_object.nick if not player_object.nick is None else player_object.name
                await ctx.channel.send(f"Your vote against {display_name} has been noted.")
                await ctx.message.pin()

        else:
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            await ctx.channel.send(f"You are trying to vote {display_name}, but this player is dead!")
            return
    else:
        await ctx.channel.send(f"You are trying to vote {player}, but such a player is not in the game!")
        return

@vote.error
async def vote_error(ctx, error):
   if isinstance(error, commands.DisabledCommand):
       await ctx.channel.send('This command is disabled outside of a round.')

@bot.command("alliance", hidden=False)
@commands.has_role(ENV_VARS["alive-role"])
@commands.check(check_if_confessional)
@require(state="IN_ROUND")
async def alliance(ctx, name, *args):
    """A command to make an alliance
    Usage example:
        ^alliance "My new cool alliance" player1 player2 ...
    * You do not need to @ the players. Simply put their nickname, as you see them in the server.
    * You need at least 2 people other than you. You don't have to list yourself.
    * Make sure that the alliance name goes first and is in quotes.
    """

    guild = ctx.guild
    member = ctx.author

    live_players = get_yaml(PLAYER_FILE)
    round = get_yaml(GAME_STATE_FILE)['Round']
    
    players_to_add = []
    players_to_add.append(member)
    for to_add in args:
        player_object = guild.get_member_named(to_add)

        if player_object == member:
            continue

        if player_object is None:
            name_variants = get_yaml('name-variants.yaml')
            if to_add in name_variants:
                player_object = guild.get_member_named(name_variants[to_add])
            else:
                await ctx.channel.send(f"Can't find '{to_add}'. Maybe you spelled the name incorrectly?\nIf you are sure that is a correct call please ping @Host ASAP.")
                return
        
        if player_object in players_to_add:
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            await ctx.channel.send(f"You attempted to add the same player ({display_name}) twice.")
            return

        if is_dead(player_object):
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            await ctx.channel.send(f"You are attempting to add a dead player ({display_name}) to the alliance. They can't bet added.")
            return

        elif player_object.id in live_players:
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            await ctx.channel.send(f"{display_name} has been noted.")
        else:
            await ctx.channel.send(f"You are trying to add {to_add}, but such a player is not in the game!")
            return
        
        players_to_add.append(player_object)
    if len(players_to_add)<3:
        await ctx.channel.send('An alliance may only be created for 3+ players (You + at least two more).')
        return

    category = discord.utils.get(guild.categories, id=ENV_VARS['alliance-chats'])
    spectator = discord.utils.get(guild.roles, id=ENV_VARS['spectator-role'])
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        spectator: discord.PermissionOverwrite(read_messages=True, send_messages=False)
    }
    
    channel_topic = '**'
    for to_add in players_to_add:
        overwrites[to_add] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        display_name = to_add.nick if not to_add.nick is None else to_add.name
        channel_topic += display_name
        channel_topic += ', '
    #Remove last comma and space:
    channel_topic = channel_topic[:-2]
    channel_topic += f'** (Round {round})'
    
    channel = await guild.create_text_channel(name, category=category, overwrites=overwrites)
    
    
    await channel.edit(topic=channel_topic)
    alive_role = discord.utils.get(guild.roles, id=ENV_VARS["alive-role"])
    display_name = member.nick if not member.nick is None else member.name
    await channel.send(f'{alive_role.mention} Requested by {display_name}')

    alliance = {
        'name': name,
        'state': 'open',
        'members':[p.id for p in players_to_add]
    }
    
    update_yaml_file(ALLIANCE_FILE, alliance, channel.id)






    

bot.help_command = commands.DefaultHelpCommand(verify_checks=False, no_category='Player commands')

from roles import VotesAndCommands
bot.add_cog(VotesAndCommands(bot))

### Start bot
bot.run(TOKEN)
