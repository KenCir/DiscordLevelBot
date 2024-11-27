import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot


@app_commands.default_permissions(administrator=True)
class AdminSettingCommand(
    commands.GroupCog, name="setting", description="管理者用設定コマンド"
):
    role_group = app_commands.Group(name="role", description="ロール設定コマンド")

    def __init__(self, bot: DiscordLevelBot):
        self.bot = bot

    @role_group.command(name="add", description="レベルロールを追加します")
    @app_commands.describe(role="追加するロール")
    @app_commands.describe(level="追加するレベル")
    async def level_role_add(
        self, interaction: discord.Interaction, role: discord.Role, level: int
    ):
        await interaction.response.defer()

        await self.bot.db.create_guild_level_role(interaction.guild.id, role.id, level)

        await interaction.followup.send("レベルロールを追加しました")
