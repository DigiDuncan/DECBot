import json

from decbot.lib.paths import voicespath

class VoicesDB:
    def __init__(self):
        with open(voicespath, "r") as f:
            d = json.load(f)
        self.dict: dict[int, str] = {int(k): v for k, v in d.items()}

    def set_voice(self, id: int, voice: str):
        self.dict[id] = voice
        self.save()

    def get_voice(self, id: int) -> str:
        return self.dict[id] if id in self.dict else ""

    def save(self):
        with open(voicespath, "w") as f:
            json.dump({str(k): v for k, v in self.dict.items()}, f)

voicesdb = VoicesDB()