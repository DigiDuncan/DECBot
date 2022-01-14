import logging

import discord
from discord.ext import commands

from decbot.cogs.tts import queues
from decbot.lib.dec import DECMEssage, DECQueue
from decbot.lib.decutils import DECTalkException, clean_nickname, talk_to_file
from decbot.lib.filelist import FileDict, UniqueFileList
from decbot.lib.paths import channelspath, vcpath

logger = logging.getLogger("decbot")

current_vcs = FileDict(vcpath)
listening_channels = UniqueFileList(channelspath)


def is_mod():
    async def predicate(ctx):
        author = ctx.author
        modness = False
        if await ctx.bot.is_owner(author):
            modness = True
        elif author.permissions_in(ctx.channel).manage_guild:
            modness = True
        return modness
    return commands.check(predicate)


class ChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_mod()
    async def addchannel(self, ctx, channel: discord.TextChannel = None):
        """Add a channel that DECBot will read every message from.

        If the user typing is not in a channel, the message will go to
        the current set default channel (which you can set with)
        `<setvc` while in a VC."""
        if channel is None:
            channel = ctx.message.channel
        listening_channels.append(f"{ctx.guild.id}:{channel.id}")
        await ctx.send(f"Channel {channel.name} added to listened channels.")

    @commands.command()
    @is_mod()
    async def removechannel(self, ctx, channel: discord.TextChannel = None):
        """Remove a channel DECBot is listening to."""
        if channel is None:
            channel = ctx.message.channel
        try:
            listening_channels.remove(f"{ctx.guild.id}:{channel.id}")
        except ValueError:
            await ctx.send("That channel is not being listening to.")
            return
        await ctx.send(f"Channel {channel.name} removed from listened channels.")

    @commands.command()
    @is_mod()
    async def setvc(self, ctx):
        """Set the currently active VC."""
        if ctx.author.voice:
            current_vcs[ctx.guild.id] = ctx.author.voice.id
        else:
            await ctx.send("You aren't in a voice channel!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if f"{message.guild.id}:{message.channel.id}" not in listening_channels:
            return

        if message.author.id == message.guild.me.id:
            return

        if message.content.startswith("<") or message.content.startswith("?"):
            return

        if message.content == "":
            return

        v = message.author.voice
        if v is None:
            vci = current_vcs.setdefault(message.guild.id, message.guild.voice_channels[0].id)
            vc = message.guild.get_channel(vci)
        else:
            vc = v.channel

        message_text = message.clean_content
        message_author = clean_nickname(message.author.display_name)
        if message.reference:
            try:
                other_message = await message.channel.fetch_message(message.reference.message_id)
                message_author += ", replying to " + clean_nickname(other_message.author.display_name) + ","
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        # Generate the DECtalk file
        try:
            temp_file_path = await talk_to_file(message_text, message.id)
        except DECTalkException as e:
            await message.channel.send(e.message)
            return

        # Read in the audio
        audio = discord.FFmpegPCMAudio(temp_file_path)
        if audio is None:
            await message.channel.send("Failed to load the audio!")
            return

        # This shouldn't happen
        if vc is None:
            await message.channel.send("Failed to get the Voice Channel!")
            return

        vcid = vc.id
        # Make queues if we need to
        try:
            queue = queues[(message.guild.id, vcid)]
        except KeyError:
            queues[(message.guild.id, vcid)] = DECQueue(message.guild.id, vcid)
            queue = queues[(message.guild.id, vcid)]

        queue.add_to_queue(
            DECMEssage(message_author, message.author.id, message.id,
                       message_text))


def setup(bot):
    bot.add_cog(ChannelCog(bot))
