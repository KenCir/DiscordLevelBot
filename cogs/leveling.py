import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot
from utils.util import calculation_level, calculation_next_level_exp


class RankingPagination(discord.ui.View):
    def __init__(self, user: discord.User, pages: list[discord.Embed]):
        super().__init__()
        self.user = user
        self.pages = pages
        self.current_page = 0
        self.prev_button = discord.ui.Button(
            label="⬅", style=discord.ButtonStyle.primary, disabled=True
        )
        self.next_button = discord.ui.Button(
            label="➡", style=discord.ButtonStyle.primary, disabled=(len(pages) == 1)
        )
        self.close_button = discord.ui.Button(
            label="❌", style=discord.ButtonStyle.danger
        )
        self.page_label = discord.ui.Button(
            label=f"{self.current_page + 1}/{len(self.pages)}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
        )
        self.prev_button.callback = self.prev_button_callback
        self.next_button.callback = self.next_button_callback
        self.close_button.callback = self.close_button_callback
        self.add_item(self.prev_button)
        self.add_item(self.page_label)
        self.add_item(self.next_button)
        self.add_item(self.close_button)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    async def update_page(self, interaction: discord.Interaction) -> None:
        if self.current_page == 0:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False
        if self.current_page == len(self.pages) - 1:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False
        self.page_label.label = f"{self.current_page + 1}/{len(self.pages)}"
        await interaction.response.edit_message(
            embed=self.pages[self.current_page], view=self
        )

    async def prev_button_callback(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_page(interaction)

    async def next_button_callback(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
        await self.update_page(interaction)

    async def close_button_callback(self, interaction: discord.Interaction):
        self.prev_button.disabled = True
        self.next_button.disabled = True
        self.close_button.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()


class Leveling(commands.Cog):
    def __init__(self, bot: DiscordLevelBot):
        self.bot = bot
        self._locks: [int, asyncio.Lock] = {}

    async def on_message_v1(self, message: discord.Message):
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

            exp = await self.bot.db.get_user_level_v1(
                message.author.id, message.guild.id
            )
            if not exp:
                await self.bot.db.create_user_level_v1(
                    message.author.id, message.guild.id
                )
                exp = await self.bot.db.get_user_level_v1(
                    message.author.id, message.guild.id
                )
            level, _ = calculation_level(exp)
            increase_exp = random.randint(min_exp, max_exp)
            increased_exp = exp + increase_exp
            increased_level, _ = calculation_level(increased_exp)
            await self.bot.db.update_user_level_v1(
                message.author.id, message.guild.id, increased_exp
            )

            if level < increased_level:
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

            exp = await self.bot.db.get_user_level(
                message.author.id, message.guild.id, message.channel.id
            )
            if not exp:
                await self.bot.db.create_user_level(
                    message.author.id, message.guild.id, message.channel.id
                )
                exp = await self.bot.db.get_user_level_v1(
                    message.author.id, message.guild.id
                )

    @app_commands.command(name="rank", description="現在のレベルを表示します")
    @app_commands.describe(user="表示するメンバー")
    async def rank(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        user = user or interaction.user
        exp = await self.bot.db.get_user_level_v1(user.id, interaction.guild.id)
        if not exp:
            await interaction.followup.send("No Data")
            return

        level, exp = calculation_level(exp)
        ranking = await self.bot.db.get_user_level_rank_v1(
            user.id, interaction.guild.id
        )
        await interaction.followup.send(
            content=f"現在`{ranking}`位\nLevel: `{level}`\nExp: `{exp}/{calculation_next_level_exp(level)}`",
        )

    @app_commands.command(name="top", description="ランキングを表示します")
    async def top(self, interaction: discord.Interaction):
        await interaction.response.defer()

        users = await self.bot.db.get_user_level_ranking_v1(interaction.guild.id)
        if len(users) == 0:
            await interaction.followup.send("No Data")
            return

        pages = []
        for i in range(0, len(users), 10):
            page = discord.Embed(
                title="ランキング",
                description="\n".join(
                    [
                        f"{i + 1}位 <@{user[0]}>\nLv. {calculation_level(user[1])[0]} Exp. {calculation_level(user[1])[1]}"
                        for i, user in enumerate(users[i : i + 10])
                    ]
                ),
            )
            pages.append(page)

        await interaction.followup.send(
            embed=pages[0], view=RankingPagination(interaction.user, pages)
        )

    @app_commands.command(name="rewards", description="レベルロールを表示します")
    async def rewards(self, interaction: discord.Interaction):
        await interaction.response.defer()

        level_roles = await self.bot.db.get_guild_level_roles(interaction.guild.id)
        if len(level_roles) == 0:
            await interaction.followup.send("No Data")
            return

        embed = discord.Embed(title="レベルロール報酬")
        for role in level_roles:
            embed.add_field(name=f"Level: {role[1]}", value=f"<@&{role[0]}>")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
