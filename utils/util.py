import discord
from discord import app_commands


class NotBotAdmin(app_commands.CheckFailure):
    pass


def is_bot_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id == 714455926970777602:
            return True

        raise NotBotAdmin("You are not the bot owner")

    return app_commands.check(predicate)
