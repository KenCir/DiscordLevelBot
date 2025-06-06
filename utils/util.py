import math

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


def calculation_level(exp: int) -> tuple[int, int]:
    level = 0
    while True:
        _exp = (5 * (level**2) + (50 * level) + 100) - exp
        if _exp <= 0:
            level += 1
            exp = abs(_exp)
        else:
            break

    return level, exp


def calculation_next_level_exp(level: int) -> int:
    return 5 * (level**2) + (50 * level) + 100
