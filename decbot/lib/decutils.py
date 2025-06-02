import asyncio
import importlib.resources as pkg_resources
import re

from discord.ext import commands
from emoji import demojize

import decbot.dectalk
from decbot.lib.filelist import FileDict
from decbot.lib.paths import tempdir, replacementspath
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


replacements = FileDict(replacementspath)

def perform_replacements(s):
    s = s.lower()
    for k, v in replacements.items():
        pattern = r"\b" + re.escape(k.lower()) + r"\b"
        s = re.sub(pattern, v, s)
    return s


def clean_text(s, prefix = ""):
    voice = "[:volume set 5][:np]" if not prefix else f"[:volume set 5]{prefix}"
    old_s = s
    s = remove_code_block(s)
    s = re.sub(r"(\|\|.+\|\|)[,.\?!]*", lambda x: f"[:volume set 2][:t 220,{len(x.group(1)) * 50}][:volume set 5] ", s)
    s = re.sub(r"(█+)[,.\?!]*", lambda x: f"[:volume set 2][:t 220,{len(x.group(1)) * 100}][:volume set 5] ", s)
    s = re.sub(r"((<a:k1:1073106773457776640>|<a:k2:1073106775450058762>|<a:k3:1073106776507023370>|<a:k4:1073106777513664512>)+)", lambda x: f"[:volume set 2][:t 220,{len(x.group(1)) * 8}][:volume set 5] ", s)
    s = re.sub(r"<a?:(?:123)?(.*?):\d+?>", lambda x: x.group(1).replace("_", " "), s)  # Make Discord emojis just their name.
    s = demojize(s, delimiters=("(", " emoji)"), use_aliases=True)  # Make unicode emojis just their name.
    s = re.sub(r"\(.* emoji\)", lambda x: x.group().replace("_", " ").removeprefix("(").removesuffix(")"), s)  # remove _ from emoji names
    s = s.replace("*", "")  # No *
    s = s.replace("`", "")  # No `
    s = s.replace("_", "")  # No _
    s = s.replace("\n", " [:pp 250][:pp 0] ")
    
    s = perform_replacements(s)

    s = "[:phoneme on] [:rate 200] " + prefix + s
    print(old_s, "->", s)
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
        # elif author.permissions_in(ctx.channel).manage_guild:
            # modness = True
        return modness
    return commands.check(predicate)
