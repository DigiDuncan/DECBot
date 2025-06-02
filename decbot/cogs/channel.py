import logging

import discord
from discord.ext import commands

from decbot.cogs.tts import queues
from decbot.lib.dec import DECMEssage, DECQueue
from decbot.lib.decutils import DECTalkException, clean_nickname, is_mod, talk_to_file
from decbot.lib.filelist import FileDict, UniqueFileList
from decbot.lib.paths import channelspath, vcpath
from decbot.lib.voices import namesdb

logger = logging.getLogger("decbot")

current_vcs = FileDict(vcpath)
listening_channels = UniqueFileList(channelspath)


class ChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot

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
            current_vcs[ctx.guild.id] = ctx.author.voice.channel.id
        else:
            await ctx.send("You aren't in a voice channel!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == message.guild.me.id:
            return

        # Trying to deal with the Suki issue
        bot_name = None
        if message.author.bot and message.author.id != 1055993189640704020:
            bot_name = message.author.name if namesdb.get_name(message.author.id) is None else namesdb.get_name(message.author.id)
            async for m in message.channel.history(limit=10, before = message.created_at):
                message.author = m.author
                break
        # IRIS AAA
        elif message.author.id == 1055993189640704020:
            bot_name = "Iris"
            message.author = message.guild.get_member(403269334065217547)  # it's baker

        if f"{message.guild.id}:{message.channel.id}" not in listening_channels:
            return

        if message.clean_content.startswith("?"):  # Suki
            return

        if message.clean_content.startswith("<") and not message.clean_content.startswith("<:") and not message.clean_content.startswith("<a:"):  # no read please
            return

        if message.content == "":
            return

        if "http" in message.content:
            return

        try:
            v = message.author.voice
        except AttributeError:
            return

        if v is None:
            return
            vci = current_vcs.setdefault(message.guild.id, message.guild.voice_channels[0].id)
            vc = message.guild.get_channel(vci)
        else:
            vc = v.channel

        if message.stickers:
            print(f"Found stickers: {message.stickers}")
            message_text = message.stickers[0].name
        else:
            message_text = message.clean_content
        m_nick = namesdb.get_name(message.author.id) if bot_name is None else bot_name
        message_author = clean_nickname(message.author.display_name) if m_nick is None else m_nick
        if message.reference:
            try:
                other_message = await message.channel.fetch_message(message.reference.message_id)
                other_name = namesdb.get_name(other_message.author.id) or clean_nickname(other_message.author.display_name)
                message_author += ", replying to " + other_name + ","
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        if message.author.id == 403269334065217547:  # 4Bakers
            if message_text.startswith(">>"):  # Iris
                if message.guild.id in [1041121893425631312, 733861887078563861, 1164580827443765309]:  # servers with the Iris bot in them
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
            temp_file_path = await talk_to_file(message_text, message.author.id, message.id)
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
            queue = queues[message.guild.id]
        except KeyError:
            queues[message.guild.id] = DECQueue(message.guild.id)
            logger.info(f"Created queue {message.guild.id}")
            queue = queues[message.guild.id]

        queue.add_to_queue(
            DECMEssage(message_author, message.author.id, message.id,
                       message_text, vcid))
        logger.info(f"Adding message {message.id} to queue {(message.guild.id, vcid)}")


async def setup(bot):
    await bot.add_cog(ChannelCog(bot))
