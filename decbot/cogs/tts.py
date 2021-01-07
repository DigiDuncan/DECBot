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
    async def tts(self, ctx, *, message):
        message = "[:phoneme on] " + message
        await ctx.send(f"If I were working, I would say: ```\n{message}\n```")

    @commands.command(
        aliases = ["file"],
        hidden = True,
        multiline = True
    )
    async def wav(self, ctx, *, message):
        message = "[:phoneme on] " + message
        await ctx.send(f"If I were working, I would send a file saying: ```\n{message}\n```")


def setup(bot):
    bot.add_cog(TTSCog(bot))
