import asyncio

from discord.voice_client import VoiceClient


# Wrap the callback version in a function that returns a future
def play_until_done_future(voiceclient, source):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    def after(err):
        if err:
            fut.set_exception(err)
            return
        fut.set_result(None)

    voiceclient.play(source, after=after)

    return fut


# Wrap the future version in a coroutine
async def play_until_done(self, source):
    return await play_until_done_future(self, source)


def patch():
    VoiceClient.play_until_done = play_until_done
