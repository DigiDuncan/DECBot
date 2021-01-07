import logging

from discord.ext import commands

logger = logging.getLogger("decbot")


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases = ["t", "say"],
        hidden = True,
        multiline = True
    )
    @commands.is_owner()
    async def tts(self, ctx, *, message):
        await ctx.send(f"If I were working, I would say: ```\n{message}\n```")


def setup(bot):
    bot.add_cog(TTSCog(bot))
