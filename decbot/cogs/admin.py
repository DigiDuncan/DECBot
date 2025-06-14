import logging

from discord.ext import commands

from decbot.lib.markdown import parse_string_to_spans

logger = logging.getLogger("decbot")


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def kill(self, ctx):
        """RIP DECBot."""
        logger.critical(f"Help, {ctx.author.display_name} is closing me!")
        await ctx.send("Stopping DECBot. ☠️")
        await ctx.bot.close()

    @commands.command()
    async def parse(self, ctx, *, s: str):
        spans = parse_string_to_spans(s)
        message = ""
        for span in spans:
            message += f"**{span.text}** "
            if span.bold or span.italics or span.spoiler or span.strikethrough or span.underline or span.header_level or span.link or span.insert or span.code:
                message += "*("
                if span.bold:
                    message += "bold, "
                if span.italics:
                    message += "italics, "
                if span.spoiler:
                    message += "spoiler, "
                if span.strikethrough:
                    message += "strikethrough, "
                if span.underline:
                    message += "underline, "
                if span.code:
                    message += "code, "
                if span.link:
                    message += "link, "
                if span.insert:
                    message += "insert, "
                if span.header_level:
                    message += "header " + str(span.header_level)
                message = message.rstrip()
                message = message.removesuffix(",")
                message += ")*"
            message += "\n"
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
