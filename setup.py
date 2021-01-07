import re
from pathlib import Path
import setuptools


def getLongDescription():
    with open("README.md", "r") as fh:
        longDescription = fh.read()
    return longDescription


# Parse the requirements.txt file for requirements (package==version) and dependencies (git+git://myrepo@branch)
def getRequirements():
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    return requirements


def getVersion(package):
    path = Path(__file__).parent.resolve() / package / "__init__.py"
    with open(path, "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if not version_match:
        raise RuntimeError("Unable to find version string.")
    version = version_match.group(1)
    return version


setuptools.setup(
    name="DECBot",
    version=getVersion("decbot"),
    author="DigiDuncan",
    author_email="digiduncan@gmail.com",
    description="DECTalk TTS for Discord, with additional features.",
    long_description=getLongDescription(),
    long_description_content_type="text/markdown",
    url="https://github.com/DigiDuncan/DECBot",
    python_requires=">=3.8",
    install_requires=getRequirements(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    entry_points={
        "console_scripts": [
            "decbot=decbot.main:main"
        ]
    }
)
