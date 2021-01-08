import importlib.resources as pkg_resources

import toml

import decbot.data
from decbot.lib.attrdict import AttrDict

emojis = None


def loademojis(data):
    global emojis
    # Get the ids dictionary (or an empty dict if none exists)
    emojisdict = data.get("emojis", {})
    # make all names lowercase
    emojisdict = {name.lower(): emoji for name, emoji in emojisdict.items()}
    # create the enum
    emojis = AttrDict(emojisdict)


def load():
    # Load constants toml file
    data = toml.loads(pkg_resources.read_text(decbot.data, "constants.ini"))
    loademojis(data)


load()
