import asyncio
import importlib.resources as pkg_resources
import re
import unicodedata

import discord
from discord.ext import commands
from emoji import demojize

import decbot.dectalk
from decbot.lib.paths import tempdir
from decbot.lib.utils import remove_code_block
from decbot.lib.voices import voicesdb


class DECTalkException(Exception):
    pass


class DECTalkReturnCodeException(DECTalkException):
    def __init__(self, code=None):
        self.code = code
        message = f"`say.exe` failed with return code **{code}**"
        super().__init__(message)


class NoAudioException(DECTalkException):
    def __init__(self):
        message = "Audio failed to load!"
        super().__init__(message)


def clean_text(s, prefix = ""):
    s = remove_code_block(s)
    s = re.sub(r"<a?:(.*?):\d+?>", r"\1 ", s)  # Make Discord emojis just their name.
    s = demojize(s, delimiters=("(", " emoji)"), use_aliases=True)  # Make unicode emojis just their name.
    s = re.sub(r"\(.* emoji\)", lambda x: x.group().replace("_", " ").removeprefix("(").removesuffix(")"), s)  # remove _ from emoji names
    s = re.sub(r"\*", "", s)  # No *
    s = s.replace("\n", " [:pp 333][:pp 0] ")
    s = "[:phoneme on] [:rate 150] " + prefix + s
    return s


def clean_nickname(nick: str):
    return re.sub(R"\[.*\]", "", nick)


async def talk_to_file(s, author_id, filename):
    voice = voicesdb.get_voice(author_id)
    s = clean_text(s, voice)

    # Make the temp directory if it's not there.
    tempdir.mkdir(exist_ok=True, parents=True)

    # Run the say process with the input parameters.
    with pkg_resources.path(decbot.dectalk, "say.exe") as say_path:
        temp_file_path = tempdir / f"{filename}.wav"
        process = await asyncio.create_subprocess_exec(say_path, "-w", str(temp_file_path), s, cwd=say_path.parent)
        await process.wait()

    # Raise exceptions if we mess up.
    if process.returncode != 0:
        raise DECTalkReturnCodeException(f"`say.exe` failed with return code **{process.returncode}**", code=process.returncode)
    if not temp_file_path.exists():
        raise DECTalkException(f"File was not created: {temp_file_path}")

    return temp_file_path


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