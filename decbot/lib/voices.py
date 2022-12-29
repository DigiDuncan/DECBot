import json

from decbot.lib.paths import voicespath, namespath

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

    def reset_voice(self, id: int) -> str:
        self.dict.pop(id)
        self.save()

    def save(self):
        with open(voicespath, "w") as f:
            json.dump({str(k): v for k, v in self.dict.items()}, f)

voicesdb = VoicesDB()

class NamesDB:
    def __init__(self):
        with open(namespath, "r") as f:
            d = json.load(f)
        self.dict: dict[int, str] = {int(k): v for k, v in d.items()}

    def set_name(self, id: int, name: str):
        self.dict[id] = name
        self.save()

    def reset_name(self, id: int):
        self.dict.popitem(id)
        self.save()

    def get_name(self, id: int) -> str:
        return self.dict[id] if id in self.dict else None

    def save(self):
        with open(namespath, "w") as f:
            json.dump({str(k): v for k, v in self.dict.items()}, f)

namesdb = NamesDB()