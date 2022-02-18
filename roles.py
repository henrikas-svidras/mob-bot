import discord
from discord.ext import commands
from mob_library.caching import get_yaml

from mob_library.helpers import WrongRoleError

env = get_yaml("env.yaml")
PLAYER_FILE = env['player-file']

ABILITIES_CHANNEL = 879053321900523521

class VotesAndCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_name = None

    @commands.command()
    async def Swap(self, ctx):
        players = get_yaml(PLAYER_FILE)
        discord_server = ctx.guild
        callers_role = players[ctx.author.id]['role']
        if callers_role != 'Houdini':
            raise WrongRoleError
        channel = discord.utils.get(discord_server.channels, id=ABILITIES_CHANNEL)

        await channel.send("Swap clap pow")
    
    @commands.command()
    async def Scan(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Avenge(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Raise(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Smuggle(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Quarantine(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Pull(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Brew(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Shuffle(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Divide(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Cast(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Cast(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Flee(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Gift(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Order(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Link(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Reset(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Reset(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Torture(self, ctx):
        raise NotImplementedError
    
    @commands.command()
    async def Shed(self, ctx):
        raise NotImplementedError