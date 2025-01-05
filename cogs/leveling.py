import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot
from utils.util import calculation_level, calculation_next_level_exp


class RankingPagination(discord.ui.View):
    def __init__(
        self,
        bot: DiscordLevelBot,
        user: discord.User,
        top_members_pages: list[discord.Embed],
        top_channels_pages: list[discord.Embed],
    ):
        super().__init__()
        self.bot = bot
        self.user = user
        self.pages = top_members_pages
        self.top_members_pages = top_members_pages
        self.top_channels_pages = top_channels_pages
        self.current_page = 0
        self.dropdown = discord.ui.Select(
            placeholder="Select a page",
            options=[
                discord.SelectOption(label=f"Top Members", value="top_members"),
                discord.SelectOption(
                    label=f"Top Members in Channel",
                    value="top_members_in_channel",
                ),
                discord.SelectOption(
                    label=f"Top Channels",
                    value="top_channels",
                ),
            ],
        )
        self.channel_select = discord.ui.ChannelSelect(
            placeholder="Select a channel",
            channel_types=[discord.ChannelType.text],
        )
        self.prev_button = discord.ui.Button(
            label="⬅", style=discord.ButtonStyle.primary, disabled=True
        )
        self.next_button = discord.ui.Button(
            label="➡",
            style=discord.ButtonStyle.primary,
            disabled=(len(self.pages) == 1),
        )
        self.page_label = discord.ui.Button(
            label=f"{self.current_page + 1}/{len(self.pages)}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
        )
        self.dropdown.callback = self.dropdown_callback
        self.channel_select.callback = self.channel_select_callback
        self.prev_button.callback = self.prev_button_callback
        self.next_button.callback = self.next_button_callback
        self.add_item(self.dropdown)
        self.add_item(self.prev_button)
        self.add_item(self.page_label)
        self.add_item(self.next_button)

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

    async def dropdown_callback(self, interaction: discord.Interaction):
        selected = self.dropdown.values[0]
        if selected == "top_members":
            self.pages = self.top_members_pages
            self.current_page = 0
        elif selected == "top_members_in_channel":
            self.pages = [discord.Embed(description="チャンネルを選択してください")]
            self.current_page = 0
            self.add_item(self.channel_select)
            self.remove_item(self.prev_button)
            self.remove_item(self.page_label)
            self.remove_item(self.next_button)
        elif selected == "top_channels":
            self.pages = self.top_channels_pages
            self.current_page = 0

        await self.update_page(interaction)

    async def channel_select_callback(self, interaction: discord.Interaction):
        selected_channel = self.channel_select.values[0]
        top_members_in_channel = await self.bot.db.get_user_level_ranking(
            interaction.guild.id, selected_channel.id
        )
        top_members_in_channel_pages = []
        for i in range(0, len(top_members_in_channel), 10):
            page = discord.Embed(
                title=f"チャンネルランキング {selected_channel.name}",
                description="\n".join(
                    [
                        f"{ranking}位 <@{user_id}> Exp. {exp}"
                        for user_id, exp, ranking in top_members_in_channel[i : i + 10]
                    ]
                ),
            )
            top_members_in_channel_pages.append(page)

        if len(top_members_in_channel_pages) == 0:
            top_members_in_channel_pages = [discord.Embed(description="No Data")]

        self.pages = top_members_in_channel_pages
        self.current_page = 0
        self.remove_item(self.channel_select)
        self.add_item(self.prev_button)
        self.add_item(self.page_label)
        self.add_item(self.next_button)
        await self.update_page(interaction)

    async def prev_button_callback(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_page(interaction)

    async def next_button_callback(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
        await self.update_page(interaction)


class RankEmbedPage(discord.ui.View):
    def __init__(
        self,
        user: discord.User,
        stats_embed: discord.Embed,
        top_channels_embeds: list[discord.Embed],
    ):
        super().__init__()
        self.user = user
        self.stats_embed = stats_embed
        self.top_channels_embed = top_channels_embeds[0]
        self.top_channels_pages = top_channels_embeds
        self.top_channels_current_page = 0
        self.stats_button = discord.ui.Button(
            label="Stats", style=discord.ButtonStyle.primary, disabled=True
        )
        self.top_channels_button = discord.ui.Button(
            label="Top Channels", style=discord.ButtonStyle.secondary
        )
        self.prev_button = discord.ui.Button(
            label="⬅", style=discord.ButtonStyle.primary, disabled=True, row=1
        )
        self.next_button = discord.ui.Button(
            label="➡",
            style=discord.ButtonStyle.primary,
            disabled=(len(self.top_channels_pages) == 1),
            row=1,
        )
        self.page_label = discord.ui.Button(
            label=f"{self.top_channels_current_page + 1}/{len(self.top_channels_pages)}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=1,
        )
        self.stats_button.callback = self.stats_button_callback
        self.top_channels_button.callback = self.top_channels_button_callback
        self.prev_button.callback = self.top_channels_prev_button_callback
        self.next_button.callback = self.top_channels_next_button_callback
        self.add_item(self.stats_button)
        self.add_item(self.top_channels_button)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    async def stats_button_callback(self, interaction: discord.Interaction):
        self.stats_button.disabled = True
        self.stats_button.style = discord.ButtonStyle.primary
        self.top_channels_button.disabled = False
        self.top_channels_button.style = discord.ButtonStyle.secondary
        self.remove_item(self.prev_button)
        self.remove_item(self.page_label)
        self.remove_item(self.next_button)
        await interaction.response.edit_message(embed=self.stats_embed, view=self)

    async def top_channels_button_callback(self, interaction: discord.Interaction):
        self.stats_button.disabled = False
        self.stats_button.style = discord.ButtonStyle.secondary
        self.top_channels_button.disabled = True
        self.top_channels_button.style = discord.ButtonStyle.primary
        self.add_item(self.prev_button)
        self.add_item(self.page_label)
        self.add_item(self.next_button)
        await interaction.response.edit_message(
            embed=self.top_channels_embed, view=self
        )

    async def top_channels_update_page(self, interaction: discord.Interaction) -> None:
        if self.top_channels_current_page == 0:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False
        if self.top_channels_current_page == len(self.top_channels_pages) - 1:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False
        self.page_label.label = (
            f"{self.top_channels_current_page + 1}/{len(self.top_channels_pages)}"
        )
        await interaction.response.edit_message(
            embed=self.top_channels_pages[self.top_channels_current_page], view=self
        )

    async def top_channels_prev_button_callback(self, interaction: discord.Interaction):
        if self.top_channels_current_page > 0:
            self.top_channels_current_page -= 1
        await self.top_channels_update_page(interaction)

    async def top_channels_next_button_callback(self, interaction: discord.Interaction):
        if self.top_channels_current_page < len(self.top_channels_pages) - 1:
            self.top_channels_current_page += 1
        await self.top_channels_update_page(interaction)


class Leveling(commands.Cog):
    def __init__(self, bot: DiscordLevelBot):
        self.bot = bot
        self._locks: [int, asyncio.Lock] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or message.is_system():
            return

        lock = self._locks.get(message.author.id)
        if not lock:
            self._locks[message.author.id] = lock = asyncio.Lock()

        async with lock:
            guild_setting = await self.bot.db.get_guild_setting(message.guild.id)
            min_exp, max_exp, stack_level_roles = guild_setting

            exp = await self.bot.db.get_user_level_total(
                message.author.id, message.guild.id
            )
            level, _ = calculation_level(exp)
            increase_exp = random.randint(min_exp, max_exp)
            increased_exp = exp + increase_exp
            increased_level, _ = calculation_level(increased_exp)
            await self.bot.db.update_user_level(
                message.author.id, message.guild.id, message.channel.id, increase_exp
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

    @app_commands.command(name="rank", description="現在のレベルを表示します")
    @app_commands.describe(user="表示するメンバー")
    async def rank(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        user = user or interaction.user
        exp = await self.bot.db.get_user_level_total(user.id, interaction.guild.id)
        if not exp:
            await interaction.followup.send("No Data")
            return

        level, exp = calculation_level(exp)
        ranking = await self.bot.db.get_user_level_rank_total(
            user.id, interaction.guild.id
        )
        stats_embed = discord.Embed(
            description=f"現在**{ranking}位**\nLevel: `{level}`\nExp: `{exp}/{calculation_next_level_exp(level)}`"
        )
        stats_embed.set_author(
            name=f"{user.display_name}のランクカード", icon_url=user.avatar.url
        )
        top_channels = await self.bot.db.get_user_level_ranking_channel(
            user.id, interaction.guild.id
        )
        top_channels_pages = []
        for i in range(0, len(top_channels), 10):
            page = discord.Embed(
                title="チャンネルランキング",
                description="\n".join(
                    [
                        f"{ranking}位 <#{channel_id}> Exp. {exp}"
                        for channel_id, exp, ranking in top_channels[i : i + 10]
                    ]
                ),
            )
            top_channels_pages.append(page)
        await interaction.followup.send(
            embed=stats_embed, view=RankEmbedPage(user, stats_embed, top_channels_pages)
        )

    @app_commands.command(name="top", description="ランキングを表示します")
    async def top(self, interaction: discord.Interaction):
        await interaction.response.defer()

        users = await self.bot.db.get_user_level_ranking_total(interaction.guild.id)
        if len(users) == 0:
            await interaction.followup.send("No Data")
            return

        top_members_pages = []
        for i in range(0, len(users), 10):
            page = discord.Embed(
                title="ランキング",
                description="\n".join(
                    [
                        f"{ranking}位 <@{user_id}>\nLv. {calculation_level(exp)[0]} Exp. {calculation_level(exp)[1]}"
                        for user_id, exp, ranking in users[i : i + 10]
                    ]
                ),
            )
            top_members_pages.append(page)

        top_channels = await self.bot.db.get_user_level_ranking_total_channel(
            interaction.guild.id
        )
        top_channels_pages = []
        for i in range(0, len(top_channels), 10):
            page = discord.Embed(
                title="チャンネルランキング",
                description="\n".join(
                    [
                        f"{ranking}位 <#{channel_id}> Exp. {exp}"
                        for channel_id, exp, ranking in top_channels[i : i + 10]
                    ]
                ),
            )
            top_channels_pages.append(page)

        await interaction.followup.send(
            embed=top_members_pages[0],
            view=RankingPagination(
                self.bot, interaction.user, top_members_pages, top_channels_pages
            ),
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
