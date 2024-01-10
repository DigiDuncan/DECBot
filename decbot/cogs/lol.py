import importlib.resources as pkg_resources
import logging
import time

import discord
from discord.ext import commands

import decbot.data

logger = logging.getLogger("decbot")


class LOLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def digipee(self, ctx: commands.Context):
        """Digi also has to pee."""
        # Gets voice channel of message author
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if voice_channel is not None:
            vc = await voice_channel.connect()
            with pkg_resources.path(decbot.data, "digipee.mp3") as digipee:
                vc.play(discord.FFmpegPCMAudio(source=digipee))
            # Sleep while audio is playing.
            while vc.is_playing():
                time.sleep(.1)
            time.sleep(3)
            await vc.disconnect()
        else:
            await ctx.send(str(ctx.author.name) + "is not in a channel.")

    # @commands.command()
    # async def thething(self, ctx: commands.Context):
    #     """It's doing the thing!."""
    #     logger.error("Ah fuck, I did the thing!")
    #     await ctx.send("Logged incidence of the thing.")


async def setup(bot):
    await bot.add_cog(LOLCog(bot))
