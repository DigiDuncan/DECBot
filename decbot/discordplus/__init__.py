from decbot.discordplus import bot, command, embed, member, client, messageable, snowflake, voiceclient


def patch():
    embed.patch()
    command.patch()
    member.patch()
    bot.patch()
    client.patch()
    messageable.patch()
    snowflake.patch()
    voiceclient.patch()
