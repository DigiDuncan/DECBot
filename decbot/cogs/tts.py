import logging

import discord
from discord import File
from discord.ext import commands

from decbot.lib.decutils import talk_to_file, DECTalkException


logger = logging.getLogger("decbot")


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases = ["t", "say", "dec"],
        multiline = True
    )
    async def tts(self, ctx, *, s):
        """Say something with DECTalk in a voice channel!"""
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        # Generate the DECtalk file
        try:
            temp_file_path = await talk_to_file(ctx.message.clean_content.removeprefix(f"{ctx.prefix}{ctx.invoked_with} "), ctx.message.id)
        except DECTalkException as e:
            await ctx.send(e.message)
            return

        # Read in the audio
        audio = discord.FFmpegPCMAudio(temp_file_path)
        if audio is None:
            await ctx.send("Failed to load the audio!")
            return

        # This shouldn't happen
        if ctx.author.voice.channel is None:
            await ctx.send("Failed to get the Voice Channel!")
            return

        # Get the current voice connection, or connect if not in one
        vc = ctx.guild.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()

        # Give up, if the bot is already in a different voice channel
        if vc.channel != ctx.author.voice.channel:
            await ctx.send("I'm in another channel.")
            return

        # Give up, if the bot is currently saying something
        if vc.is_playing():
            await ctx.send("Sorry, I'm kinda busy right now.")
            return

        # Play the message, then disconnect
        await vc.play_until_done(audio)
        await vc.disconnect()

    @commands.command(
        aliases = ["file"],
        multiline = True
    )
    async def wav(self, ctx, *, s):
        """Say something with DECTalk, and send a file!"""
        try:
            temp_file_path = await talk_to_file(ctx.message.clean_content.removeprefix(f"{ctx.prefix}{ctx.invoked_with} "), ctx.message.id)
        except DECTalkException as e:
            await ctx.send(f"`say.exe` failed with return code **{e.code}**")
            return

        # If we succeed in running it, send the file.
        try:
            with temp_file_path.open("rb") as f:
                await ctx.send(file = File(f, f"{ctx.message.id}.wav"))
        except FileNotFoundError:
            await ctx.send("Uh, it looks like I didn't actually make a file.")

    @commands.command(
        aliases = ["guide"]
    )
    async def manual(self, ctx):
        await ctx.send("https://manualzz.com/doc/7326177/dectalk-5.01-e1-user-guide")

    @commands.command(
        aliases = ["shutup"],
        hidden = True,
        multiline = True
    )
    async def stop(self, ctx):
        """Shut up shut up shut up shut up"""
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("I'm not in a voice channel...")
            return
        await vc.disconnect()
        await ctx.send("...")


def setup(bot):
    bot.add_cog(TTSCog(bot))
