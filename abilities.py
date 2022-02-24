class Enchanter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('enchant')
    def enchant(self, ctx):
        await ctx.send("something")

bot.add_cog(Enchanter(bot))
