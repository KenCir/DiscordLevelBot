import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot
from utils.util import calculation_level, calculation_next_level_exp


class Leveling(commands.Cog):
    def __init__(self, bot: DiscordLevelBot):
        self.bot = bot
        self._locks: [int, asyncio.Lock] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        lock = self._locks.get(message.author.id)
        if not lock:
            self._locks[message.author.id] = lock = asyncio.Lock()

        async with lock:
            guild_setting = await self.bot.db.get_guild_setting(message.guild.id)
            if not guild_setting:
                await self.bot.db.create_guild_setting(message.guild.id)
                guild_setting = await self.bot.db.get_guild_setting(message.guild.id)
            min_exp, max_exp, stack_level_roles = guild_setting

            user_level = await self.bot.db.get_user_level(
                message.author.id, message.guild.id
            )
            if not user_level:
                await self.bot.db.create_user_level(message.author.id, message.guild.id)
                user_level = await self.bot.db.get_user_level(
                    message.author.id, message.guild.id
                )
            level, exp = user_level
            increase_exp = random.randint(min_exp, max_exp)
            increased_exp = exp + increase_exp
            increased_level = calculation_level(increased_exp)

            if level < increased_level:
                await self.bot.db.update_user_level(
                    message.author.id, message.guild.id, increased_level, 0
                )

                await message.channel.send(
                    f"{message.author.mention} LEVEL UP! `{level}` -> `{increased_level}`"
                )

                level_roles = await self.bot.db.get_guild_level_roles(message.guild.id)
                add_level_roles = list(
                    filter(lambda r: r[1] == increased_level, level_roles)
                )
                if len(add_level_roles) == 0:
                    return

                for role in add_level_roles:
                    await message.author.add_roles(discord.Object(id=role[0]))
                if not stack_level_roles:
                    remove_level_roles = list(
                        filter(lambda r: r[1] != increased_level, level_roles)
                    )
                    for role in remove_level_roles:
                        await message.author.remove_roles(discord.Object(id=role[0]))
            else:
                await self.bot.db.update_user_level(
                    message.author.id, message.guild.id, increased_level, increased_exp
                )

    @app_commands.command(name="rank", description="現在のレベルを表示します")
    @app_commands.describe(user="表示するメンバー")
    async def rank(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        user = user or interaction.user
        user_level = await self.bot.db.get_user_level(user.id, interaction.guild.id)
        if not user_level:
            await interaction.followup.send("No Data")
            return

        level, exp = user_level
        ranking = await self.bot.db.get_user_rank(user.id, interaction.guild.id)
        await interaction.followup.send(
            content=f"現在`{ranking}`位\nLevel: `{level}`\nExp: `{exp}/{calculation_next_level_exp(level)}`",
        )


async def setup(bot):
    await bot.add_cog(Leveling(bot))
