import logging
import sys

from discord.ext import commands

from decbot.lib import errors, utils
from decbot.lib.constants import emojis

logger = logging.getLogger("decbot")


def setup(bot):
    @bot.event
    async def on_command_error(ctx, error):
        # Get actual error
        err = getattr(error, "original", error)

        # If we got some bad arguments, use a generic argument exception error
        if isinstance(err, commands.BadUnionArgument) or isinstance(err, commands.MissingRequiredArgument) or isinstance(err, commands.BadArgument):
            err = errors.ArgumentException()

        if isinstance(err, commands.NotOwner):
            err = errors.AdminPermissionException()

        if isinstance(err, commands.BadMultilineCommand):
            err = errors.MultilineAsNonFirstCommandException()

        if isinstance(err, errors.DigiContextException):
            # DigiContextException handling
            message = await err.formatMessage(ctx)
            if message is not None:
                logger.log(err.level, message)
            userMessage = await err.formatUserMessage(ctx)
            if userMessage is not None:
                await ctx.send(f"{emojis.warning} {userMessage}")
        elif isinstance(err, errors.DigiException):
            # DigiException handling
            message = err.formatMessage()
            if message is not None:
                logger.log(err.level, message)
            userMessage = err.formatUserMessage()
            if userMessage is not None:
                await ctx.send(f"{emojis.warning} {userMessage}")
        elif isinstance(err, commands.errors.CommandNotFound):
            pass
        elif isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.send(f"{emojis.warning} Missing required argument(s) for `{ctx.prefix}{ctx.command}`.")
        elif isinstance(err, commands.errors.ExpectedClosingQuoteError):
            await ctx.send(f"{emojis.warning} Mismatched quotes in command.")
        elif isinstance(err, commands.errors.InvalidEndOfQuotedStringError):
            await ctx.send(f"{emojis.warning} No space after a quote in command. Are your arguments smushed together?")
        elif isinstance(err, commands.errors.UnexpectedQuoteError):
            await ctx.send(f"{emojis.warning} Why is there a quote here? I'm confused...")
        elif isinstance(err, commands.errors.CheckFailure):
            await ctx.send(f"{emojis.error} You do not have permission to run this command.")
        elif isinstance(err, commands.CommandOnCooldown):
            await ctx.send(f"{emojis.info} You're using that command too fast! Try again in a moment.")
        else:
            # Default command error handling
            await ctx.send(f"{emojis.error} Something went wrong.")
            logger.error(f"Ignoring exception in command {ctx.command}:")
            logger.error(utils.formatTraceback(error))

    @bot.event
    async def on_error(event, *args, **kwargs):
        _, error, _ = sys.exc_info()
        # Get actual error
        err = getattr(error, "original", error)
        # DigiException handling
        if isinstance(err, errors.DigiException):
            message = err.formatMessage()
            if message is not None:
                logger.log(err.level, message)
        if isinstance(err, errors.DigiContextException):
            message = str(err)
            if message is not None:
                logger.log(err.level, message)
        else:
            logger.error(f"Ignoring exception in {event}")
            logger.error(utils.formatTraceback(error))
