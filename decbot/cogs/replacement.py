import logging

from discord.ext import commands
from decbot.lib.decutils import replacements

logger = logging.getLogger("decbot")


class ReplacementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrep(self, ctx: commands.Context, k: str, v: str):
        """Set a replacement."""
        replacements[k.lower()] = v
        await ctx.send(f"'{k}' will be read as `{v}`.")

    @commands.command()
    async def removerep(self, ctx: commands.Context, *, k: str):
        """Clear a replacement."""
        replacements.pop(k)
        await ctx.send(f"Removed replacement for `{k}`.")

    @commands.command()
    async def listrep(self, ctx: commands.Context):
        """Clear a replacement."""
        await ctx.send(f"{replacements._dict}")


async def setup(bot):
    await bot.add_cog(ReplacementCog(bot))
