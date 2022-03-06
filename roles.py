import random
import discord
from discord.ext import commands
from mob_library.caching import get_yaml

from mob_library.helpers import WrongRoleError

ENV_VARS = get_yaml("env.yaml")
PLAYER_FILE = ENV_VARS['player-file']
PLAYERS = get_yaml(PLAYER_FILE)

ABILITIES_CHANNEL = ENV_VARS['abilities-channel']
HOST_ROLE = ENV_VARS['host-role']

class VotesAndCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_name = None


    @commands.command('swap')
    @commands.has_permissions(administrator=True)
    async def Swap(self, ctx, houdini, target):
        discord_server = ctx.guild
        # callers_role = PLAYERS[ctx.author.id]['role']
        # if callers_role != 'Houdini':
            # raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nSwap {houdini} with {target}.")

    @commands.command('scan')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Scan(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Tracker':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nSend ability counts to Tracker.")

    @commands.command('avenge')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Avenge(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Vigilante':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nAvenge last round's victim(s).")

    @commands.command('raise')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Raise(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Lich':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nRaise undead.")

    @commands.command('smuggle')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Smuggle(self, ctx, target):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Smuggler':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nSmuggle for {target}.")

    @commands.command('quarantine')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Quarantine(self, ctx, target1, target2, target3):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Lazar':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nQuarantine {target1}, {target2}, {target3}.")

    @commands.command('pull')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Pull(self, ctx, mostorleast):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Triggerfinger':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nKill player with {mostorleast} past votes against them at the start of next round, if Triggerfinger survives.")

    @commands.command('brew')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Brew(self, ctx, target1, type1, target2, type2):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Witch':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nBrew a {type1} Potion for {target1} and a {type2} Potion for {target2}.")

    @commands.command('shuffle')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Shuffle(self, ctx, includingexcluding):
        raise NotImplementedError # this still needs to be finished
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Gambler':
            raise WrongRoleError

        all_available_roles = ENV_VARS['available-roles']
        shuffled_roles = random.shuffle(all_available_roles)
        for player in PLAYERS:
            if (player['state'] == 'Dead') and (player['role'] in shuffled_roles):
                shuffled_roles.remove(player['role'])
        
        test_message = ""
        for n, player in enumerate(PLAYERS):
            player_object = discord.utils.get(discord_server.members, id=player)
            display_name = player_object.nick if not player_object.nick is None else player_object.name
            test_message+=display_name+f" now has a new role {shuffled_roles[n]}\n"

        
        



        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nShuffle all roles {includingexcluding} Gambler.")
        await channel.send(hostrole.mention + f"\nShuffle all roles {includingexcluding} Gambler.")

    @commands.command('divide')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Divide(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Strategist':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\n")
        raise NotImplementedError

    @commands.command('cast')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Cast(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Maniac':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\n")
        raise NotImplementedError

    @commands.command('flee')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Flee(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Outlaw':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nOutlaw flees the vote reading with 1 player receiving most votes.")
        await ctx.channel.send(f"You can no longer vote this round.")

    @commands.command('gift')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Gift(self, ctx, target):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Jeweler':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nJeweler is gifting an Opal to {target}.")

    @commands.command('order')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Order(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Canvasser':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nCanvasser is ordering a revote this round.")

    @commands.command('link')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Link(self, ctx, target, absorbornullify, number=None):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Sorcerer':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nSorcerer is linking with {target} to {absorbornullify}.\nNullifying {number} votes.")

    @commands.command('reset')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Reset(self, ctx, target):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Reverter':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nReverter is resetting {target}'s abilities.'")

    @commands.command('torture')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Torture(self, ctx, target):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Tormentor':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nTormentor is torturing {target}.")

    @commands.command('shed')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Shed(self, ctx):
        discord_server = ctx.guild
        callers_role = PLAYERS[ctx.author.id]['role']
        if callers_role != 'Hydra':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nHydra is shedding a head.")
