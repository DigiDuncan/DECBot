import logging

from discord.ext import commands

logger = logging.getLogger("decbot")


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def ping(self, ctx, *, message):
        await ctx.send("PING")


def setup(bot):
    bot.add_cog(TTSCog(bot))
