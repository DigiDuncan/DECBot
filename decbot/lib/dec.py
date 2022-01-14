from collections import deque
from dataclasses import dataclass
from typing import Union
import arrow

import discord
from decbot.lib.decutils import talk_to_file, NoAudioException


@dataclass
class DECMEssage:
    name: str
    discordid: int
    messageid: int
    message: str


class DECQueue:
    def __init__(self, guildid, vcid) -> None:
        self.guildid = guildid
        self.vcid = vcid

        self.queue = deque([])
        self.last_name: str = None
        self.audio_ended = arrow.now().timestamp
        self.talking = False

    @property
    def is_empty(self):
        return len(self.queue) == 0

    def add_to_queue(self, message: DECMEssage):
        self.queue.append(message)

    def _next(self) -> Union[DECMEssage, None]:
        try:
            return self.queue.pop()
        except IndexError:
            return None

    async def next_audio(self):
        if m := self._next():
            message = m.message
            if self.last_name != m.name:
                message = f"{m.name} says: " + message
            temp_file_path = await talk_to_file(message, m.messageid)
            audio = discord.FFmpegPCMAudio(temp_file_path)
            if audio is None:
                raise NoAudioException
            self.last_name = m.name
            return audio
        return None
