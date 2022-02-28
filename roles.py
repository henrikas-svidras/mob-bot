import discord
from discord.ext import commands
from mob_library.caching import get_yaml

from mob_library.helpers import WrongRoleError

ENV_VARS = get_yaml("env.yaml")
PLAYER_FILE = ENV_VARS['player-file']

ABILITIES_CHANNEL = ENV_VARS['abilities-channel']
HOST_ROLE = ENV_VARS['host-role']

class VotesAndCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_name = None


    @commands.command('swap')
    @commands.has_permissions(administrator=True)
    async def Swap(self, ctx, houdini, target):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        # callers_role = players[ctx.author.id]['role']
        # if callers_role != 'Houdini':
            # raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nSwap {houdini} with {target}.")

    @commands.command('scan')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Scan(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Tracker':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nTracker {caller} is scanning each player.")
        await ctx.channel.send(f"You are scanning each player for their remaining abilities.\nHosts will get back to you with the scan results soon.")
        await ctx.message.pin()

    @commands.command('avenge')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Avenge(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Vigilante':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nVigilante {caller} has avenged last round's victim(s).")
        await ctx.channel.send(f"You have avenged last round's victims.\nHosts will make an announcement as soon as possible.")
        await ctx.message.pin()

    @commands.command('raise')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Raise(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Lich':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nLich {caller} has raised an army of undead.")
        await ctx.channel.send(f"You have raised an army of undead.\nHosts will make an announcement as soon as possible.")
        await ctx.message.pin()

    @commands.command('smuggle')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Smuggle(self, ctx, target):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Smuggler':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nSmuggler {caller} is smuggling for {target}.")
        await ctx.channel.send(f"You are smuggling for {target}.")
        await ctx.message.pin()

    @commands.command('quarantine')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Quarantine(self, ctx, target1, target2, target3):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Lazar':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nLazar {caller} has quarantined {target1}, {target2} and {target3}.")
        await ctx.channel.send(f"You have quarantined {target1}, {target2} and {target3}.\nHosts will make an announcement as soon as possible.")
        await ctx.message.pin()

    @commands.command('pull')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Pull(self, ctx, mostorleast):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Triggerfinger':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nTriggerfinger {caller} is pulling their trigger on the player with {mostorleast} valid past votes against them.")
        await ctx.channel.send(f"You are pulling your trigger on the player with {mostorleast} valid past votes against them.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('brew')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Brew(self, ctx, target1, type1, target2, type2):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Witch':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nWitch {caller} has brewed a {type1} Potion for {target1} and a {type2} Potion for {target2}.")
        await ctx.channel.send(f"You have brewed a {type1} Potion for {target1} and a {type2} Potion for {target2}.\nHosts will notify the recipients as soon as possible.")
        await ctx.message.pin()

    @commands.command('shuffle')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Shuffle(self, ctx, includingexcluding):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Gambler':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nGambler {caller} has shuffled all roles {includingexcluding} their own.")
        await ctx.channel.send(f"You have shuffled all roles {includingexcluding} your own.\nHosts will take care of this as soon as possible.")
        await ctx.message.pin()

    @commands.command('divide')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Divide(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Strategist':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\n")
        raise NotImplementedError

    @commands.command('cast')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Cast(self, ctx, target, number=0):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Maniac':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"Maniac {caller} is casting {number} additional votes against {target}.")
        await ctx.channel.send(f"You have cast {number} additional votes against {target}.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('flee')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Flee(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Outlaw':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nOutlaw {caller} is fleeing with one other player receiving most valid votes.")
        await ctx.channel.send(f"You have decided to flee the vote reading, meaning, you can no longer vote.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('gift')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Gift(self, ctx, target):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Jeweler':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nJeweler {caller} has gifted an Opal to {target}.")
        await ctx.channel.send(f"You have gifted an Opal to {target}.\nHosts will notify the recipients as soon as possible.")
        await ctx.message.pin()

    @commands.command('order')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Order(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Canvasser':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nCanvasser {caller} is ordering a revote this round.")
        await ctx.channel.send(f"You are ordering a revote this round.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('link')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Link(self, ctx, target, absorbornullify, number=0):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Sorcerer':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nSorcerer {caller} is linking with {target} to {absorbornullify} – nullifying {number} votes.")
        await ctx.channel.send(f"You are linking with {target} to {absorbornullify} – nullifying {number} votes.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('reset')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Reset(self, ctx, target):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Reverter':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(hostrole.mention + f"\nReverter {caller} has reset {target}'s abilities.")
        await ctx.channel.send(f"You have reset {target}'s abilities.\nHosts will notify the recipients as soon as possible.")
        await ctx.message.pin()

    @commands.command('torture')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Torture(self, ctx, target):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Tormentor':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nTormentor {caller} is torturing {target}.")
        await ctx.channel.send(f"You are torturing {target} now.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()

    @commands.command('shed')
    @commands.has_role(ENV_VARS["alive-role"])
    async def Shed(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        caller = ctx.author.nick if not ctx.author.nick is None else ctx.author.name
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Hydra':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)
        hostrole = discord.utils.get(discord_server.roles, id=HOST_ROLE)
        await channel.send(f"\nHydra {caller} is shedding a head.")
        await ctx.channel.send(f"You are shedding a head now. This decreases your voting power.\nYou may cancel your ability before the deadline by pinging Hosts.")
        await ctx.message.pin()
