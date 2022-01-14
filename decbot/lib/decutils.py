import asyncio
import importlib.resources as pkg_resources
import re

import decbot.dectalk
from decbot.lib.paths import tempdir
from decbot.lib.utils import remove_code_block


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


def clean_text(s):
    s = remove_code_block(s)
    s = re.sub(r"<a?:(.*?):\d+?>", r"\1 ", s)  # Make emojis just their name.
    s = re.sub(r"\*", "", s)  # No *
    s = s.replace("\n", " [:pp 500][:pp 0] ")
    s = "[:phoneme on] " + s
    return s


def clean_nickname(nick: str):
    return re.sub(R"\[.*\]", "", nick)


async def talk_to_file(s, filename):
    s = clean_text(s)

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
