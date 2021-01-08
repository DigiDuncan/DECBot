import asyncio
import importlib.resources as pkg_resources
import logging
import os

from discord import File
from discord.ext import commands

import decbot.dectalk
from decbot.lib.paths import tempdir

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
        # Add phenome support to all messages.
        message = "[:phoneme on] " + message

        # Make the temp directory if it's not there.
        try:
            os.makedirs(tempdir)
        except OSError:
            pass

        # Run the say process with the input parameters.
        with pkg_resources.path(decbot.dectalk, "say.exe") as say:
            process = await asyncio.create_subprocess_exec(say.resolve(), "-w", (tempdir / f"{ctx.message.id}.wav").resolve(), message)
            await process.communicate()
            await process.wait()

        # If we succeed in running it, send the file.
        if process.returncode == 0:
            try:
                with open(tempdir / f"{ctx.message.id}.wav") as f:
                    await ctx.send(file = File(f, f"{ctx.message.id}.wav"))
            except FileNotFoundError:
                await ctx.send("Uh, it looks like I didn't actually make a file.")

        # If not, say we messed up somewhere.
        else:
            await ctx.send(f"`say.exe` failed with return code **{process.returncode}**")

        # Debug message
        await ctx.send(f"```\n{message}\n```")


def setup(bot):
    bot.add_cog(TTSCog(bot))
