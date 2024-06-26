import importlib.resources as pkg_resources
import os
import logging
from logging import DEBUG, WARN
import sys
from datetime import datetime
from pathlib import Path

import discord
from discord.ext.commands import Bot

from digiformatter import styles, logger as digilogger

import decbot.data
from decbot import __version__
from decbot import discordplus
from decbot.conf import conf
from decbot.lib import paths
from decbot.lib.loglevels import BANNER, LOGIN, CMD
from decbot.lib.utils import truncate

logging.basicConfig(level=WARN)
dfhandler = digilogger.DigiFormatterHandler()

logger = logging.getLogger("decbot")
logger.setLevel(DEBUG)
logger.handlers = []
logger.propagate = False
logger.addHandler(dfhandler)

for log in ["discord", "discord.player", "discord.voice_client", "discord.client", "discord.gateway"]:
    discordlogger = logging.getLogger(log)
    discordlogger.setLevel(logging.WARN)
    discordlogger.handlers = []
    discordlogger.propagate = True
    discordlogger.addHandler(dfhandler)

initial_cogs = ["admin", "tts", "channel", "lol", "voices", "replacement"]
initial_extensions = ["errorhandler"]

discordplus.patch()


def initConf():
    print("Initializing configuration file")
    try:
        conf.init()
        print(f"Configuration file initialized: {paths.confpath}")
    except FileExistsError as e:
        print(e)
        pass
    os.startfile(paths.confpath.parent)


def main():
    try:
        conf.load()
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e.filename}")
        confpath = Path(e.filename)
        logger.warn("Writing default settings file...")
        default_settings = pkg_resources.read_text(decbot.data, "settings.ini")
        confpath.parent.mkdir(parents = True, exist_ok = True)
        with open(confpath, "w") as f:
            f.write(default_settings)
        os.startfile(confpath.parent)
        logger.info("Please reload the bot.")
        return

    if not (
        (paths.dectalkdir / "dectalk.dll").exists()
        and (paths.dectalkdir / "say.exe").exists()
        and (paths.dectalkdir / "MSVCRTd.DLL").exists()
        and (paths.dectalkdir / "dtalk_us.dic").exists()
    ):
        logger.error(f"DECTalk installation not found. Please install a full copy of DECTalk 5 in:\n{paths.dectalkdir.resolve()}")
        return

    launchtime = datetime.now()

    bot = Bot(command_prefix = conf.prefix, intents = discord.Intents.all())

    @bot.event
    async def setup_hook():
        for extension in initial_extensions:
            await bot.load_extension("decbot.extensions." + extension)
        for cog in initial_cogs:
            await bot.load_extension("decbot.cogs." + cog)

    @bot.event
    async def on_first_ready():
        # Set the bots name to what's set in the config.
        try:
            await bot.user.edit(username = conf.name)
        except discord.errors.HTTPException:
            logger.warn("We can't change the username this much!")

        # Print the splash screen.
        # Obviously we need the banner printed in the terminal
        banner = ("decbot " + __version__)
        logger.log(BANNER, banner)
        logger.log(LOGIN, f"Logged in as: {bot.user.name} ({bot.user.id})\n------")

        # Add a special message to bot status if we are running in debug mode
        activity = discord.Game(name = "with words")
        if sys.gettrace() is not None:
            activity = discord.Activity(type=discord.ActivityType.listening, name = "DEBUGGER 🔧")

        # More splash screen.
        await bot.change_presence(activity = activity)
        print(styles)
        logger.info(f"Prefix: {conf.prefix}")
        launchfinishtime = datetime.now()
        elapsed = launchfinishtime - launchtime
        logger.info(f"DECBot launched in {round((elapsed.total_seconds() * 1000), 3)} milliseconds.\n")

    @bot.event
    async def on_reconnect_ready():
        logger.error("DECBot has been reconnected to Discord.")

    @bot.event
    async def on_command(ctx):
        guild = truncate(ctx.guild.name, 20) if (hasattr(ctx, "guild") and ctx.guild is not None) else "DM"
        logger.log(CMD, f"G {guild}, U {ctx.message.author.name}: {ctx.message.content}")

    @bot.event
    async def on_message(message):
        # F*** smart quotes.
        message.content = message.content.replace("“", "\"")
        message.content = message.content.replace("”", "\"")
        message.content = message.content.replace("’", "'")
        message.content = message.content.replace("‘", "'")

        await bot.process_commands(message)

    @bot.event
    async def on_message_edit(before, after):
        if before.content == after.content:
            return
        # TODO: This is broken with VC stuff.
        # await bot.process_commands(after)

    def on_disconnect():
        logger.error("DECBot has been disconnected from Discord!")

    if not conf.authtoken:
        logger.error("Authentication token not found!")
        return

    bot.run(conf.authtoken)
    on_disconnect()


if __name__ == "__main__":
    main()
