import logging
from typing import Dict, Tuple

import arrow
import discord
from discord import File
from discord.ext import commands, tasks

from decbot.lib.voices import namesdb

from decbot.lib.dec import DECMEssage, DECQueue
from decbot.lib.decutils import is_mod, talk_to_file, DECTalkException, clean_nickname
from decbot.lib.utils import formatTraceback


logger = logging.getLogger("decbot")

queues: Dict[Tuple[int, int], DECQueue] = {}
current_vc: Dict[int, int]


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queueTask.start()

    def cog_unload(self):
        self.queueTask.cancel()

    @commands.command(
        aliases = ["t", "say", "dec"],
        multiline = True
    )
    async def tts(self, ctx, *, s):
        """Say something with DECTalk in a voice channel!"""
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        message_text = ctx.message.clean_content.removeprefix(f"{ctx.prefix}{ctx.invoked_with} ")
        nick = namesdb.get_name(ctx.author.id)
        message_author = clean_nickname(ctx.author.display_name) if nick is None else nick
        if ctx.message.reference:
            try:
                other_message = await ctx.message.channel.fetch_message(ctx.message.reference.message_id)
                other_nick = namesdb.get_name(other_message.author.id)
                on = clean_nickname(other_message.author.display_name) if other_nick is None else other_nick
                message_author += ", replying to " + on + ","
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        if ctx.message.author.id == 403269334065217547:  # 4Bakers
            if message_text.startswith(">>"):  # Iris
                if ctx.guild.get_member(1055993189640704020):
                    return
                else:
                    message_lines = message_text.split("\n")
                    new_lines = []
                    for line in message_lines:
                        new_lines.append(line.removeprefix(">>"))
                    message_text = "\n".join(new_lines)
                    message_author = "Iris"

        # Generate the DECtalk file
        try:
            temp_file_path = await talk_to_file(message_text, ctx.author.id, ctx.message.id)
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

        vcid = ctx.message.author.voice.channel.id
        # Make queues if we need to
        try:
            queue = queues[(ctx.guild.id, vcid)]
        except KeyError:
            queues[(ctx.guild.id, vcid)] = DECQueue(ctx.guild.id, vcid)
            queue = queues[(ctx.guild.id, vcid)]

        queue.add_to_queue(
            DECMEssage(message_author, ctx.author.id, ctx.message.id,
                       message_text)
        )

    @commands.command(
        aliases = ["file"],
        multiline = True
    )
    async def wav(self, ctx, *, s):
        """Say something with DECTalk, and send a file!"""
        try:
            temp_file_path = await talk_to_file(ctx.message.clean_content.removeprefix(f"{ctx.prefix}{ctx.invoked_with} "), 0, ctx.message.id)
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
        aliases = ["shutup"]
    )
    async def stop(self, ctx):
        """Shut up shut up shut up shut up"""
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("I'm not in a voice channel...")
            return
        await vc.disconnect()
        await ctx.send("...")

    @commands.command(
        aliases = ["clear"],
        hidden = True
    )
    @is_mod()
    async def clearqueue(self, ctx):
        """Shut up shut up shut up shut up"""
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
        if ctx.author.voice.channel is None:
            await ctx.send("Failed to get the Voice Channel!")
            return
        vcid = ctx.message.author.voice.channel.id
        try:
            queue = queues[(ctx.guild.id, vcid)]
        except KeyError:
            await ctx.send("No queue exists for this channel.")
        queue.clear()
        await ctx.send("Queue cleared.")

    @tasks.loop(seconds=1)
    async def queueTask(self):
        """Queue checker"""
        qs = [q for q in queues.values() if not q.is_empty]
        discons = [q for q in queues.values() if q.audio_ended + 120 < arrow.now().timestamp()]

        for q in discons:
            vc = self.bot.get_guild(q.guildid).voice_client
            if vc:
                await vc.disconnect()

        if not qs:
            return
        try:
            for q in qs:
                vc = self.bot.get_guild(q.guildid).voice_client
                correct_channel = self.bot.get_guild(q.guildid).get_channel(q.vcid)
                if vc and vc.channel != correct_channel:
                    while q.talking:
                        pass
                if vc is None:
                    vc = await self.bot.get_guild(q.guildid).get_channel(q.vcid).connect()

                audio = await q.next_audio()

                # Play the message
                q.talking = True
                await vc.play_until_done(audio)
                q.audio_ended = arrow.now().timestamp()
                q.talking = False

        except Exception as err:
            logger.error(formatTraceback(err))

    @queueTask.before_loop
    async def before_queueTask(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(TTSCog(bot))
