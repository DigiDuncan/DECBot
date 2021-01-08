import logging

from decbot.lib import utils


# error.message will be printed when you do print(error)
# error.user_message will be displayed to the user
class DigiException(Exception):
    level = logging.WARNING

    def formatMessage(self):
        return None

    def formatUserMessage(self):
        return None

    def __repr__(self):
        return utils.getFullname(self)

    def __str__(self):
        return self.formatMessage() or self.formatUserMessage() or repr(self)


class DigiContextException(Exception):
    level = logging.WARNING

    async def formatMessage(self, ctx):
        return None

    async def formatUserMessage(self, ctx):
        return None

    def __repr__(self):
        return utils.getFullname(self)

    def __str__(self):
        return repr(self)


class NoPermissionsException(DigiException):
    level = logging.ERROR

    def formatMessage(self):
        return "DECBot does not have the permssions to perform this action."


class AdminPermissionException(DigiContextException):
    async def formatMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run an admin command."

    async def formatUserMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run an admin command. This incident will be reported."


class MultilineAsNonFirstCommandException(DigiContextException):
    async def formatMessage(self, ctx):
        usernick = ctx.author.display_name
        return f"{usernick} tried to run a multi-line command in the middle of a sequence."

    async def formatUserMessage(self, ctx):
        return "You are unable to run a command that takes a multi-line argument in the middle of a batch command sequence. Please try running these commands seperately."


class ArgumentException(DigiContextException):
    async def formatUserMessage(self, ctx):
        return f"Please enter `{ctx.prefix}{ctx.invoked_with} {ctx.command.signature}`."


class UserMessedUpException(DigiException):
    def __init__(self, custommessage):
        self.custommessage = custommessage

    def formatMessage(self):
        return self.custommessage

    def formatUserMessage(self):
        return self.custommessage


class ThisShouldNeverHappenException(DigiException):
    level = logging.CRITICAL

    def __init__(self, custommessage):
        self.custommessage = custommessage

    def formatUserMessage(self):
        return "This should never happen. Something very wrong has occured."

    def formatMessage(self):
        return self.custommessage
