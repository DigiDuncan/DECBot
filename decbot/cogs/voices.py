import logging

import discord
from discord.ext import commands
from decbot.lib.decutils import is_mod

from decbot.lib.voices import voicesdb

logger = logging.getLogger("decbot")


class VoicesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setvoice(self, ctx: commands.Context, *, voice: str):
        """Set your voice."""
        voicesdb.set_voice(ctx.author.id, voice)
        await ctx.send(f"Voice set to `{voice}`.")

    @commands.command()
    async def clearvoice(self, ctx: commands.Context):
        """Clear your voice."""
        voicesdb.set_voice(ctx.author.id, "")
        await ctx.send("Voice cleared.")

    @commands.command()
    @is_mod()
    async def resetvoice(self, ctx: commands.Context, *, member: discord.Member):
        """Clear your voice."""
        voicesdb.set_voice(member.id, "")
        await ctx.send(f"Voice cleared for {member.display_name}.")


def setup(bot):
    bot.add_cog(VoicesCog(bot))
