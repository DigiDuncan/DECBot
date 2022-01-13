import importlib.resources as pkg_resources
from pathlib import Path

import appdirs

import decbot.dectalk


def getDataDir():
    appname = "DECBot"
    appauthor = "DigiDuncan"
    datadir = Path(appdirs.user_data_dir(appname, appauthor))
    return datadir


# File paths
datadir = getDataDir()
confpath = datadir / "decbot.conf"
tempdir = datadir / "temp"
channelspath = datadir / "channels.txt"
vcpath = datadir / "vc.txt"
with pkg_resources.path(decbot.dectalk, "README.md") as dtreadme:
    dectalkdir = dtreadme.parent
