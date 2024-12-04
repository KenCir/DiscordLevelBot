import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot


@app_commands.default_permissions(administrator=True)
class AdminSettingCommand(
    commands.GroupCog, name="settings", description="管理者用設定コマンド"
):
    role_group = app_commands.Group(name="role", description="ロール設定コマンド")
    exp_group = app_commands.Group(name="exp", description="経験値設定コマンド")

    def __init__(self, bot: DiscordLevelBot):
        self.bot = bot

    @role_group.command(name="add", description="レベルロールを追加します")
    @app_commands.describe(role="追加するロール")
    @app_commands.describe(level="追加するレベル")
    async def level_role_add(
        self, interaction: discord.Interaction, role: discord.Role, level: int
    ):
        await interaction.response.defer()
        if level < 1:
            await interaction.followup.send("レベルは1以上で指定してください")
            return
        check = await self.bot.db.get_guild_level_role(interaction.guild.id, role.id)
        if check:
            await interaction.followup.send("すでに追加されているロールです")
            return
        await self.bot.db.create_guild_level_role(interaction.guild.id, role.id, level)
        await interaction.followup.send("レベルロールを追加しました")

    @role_group.command(name="remove", description="レベルロールを削除します")
    @app_commands.describe(role="削除するロール")
    async def level_role_remove(
        self, interaction: discord.Interaction, role: discord.Role
    ):
        await interaction.response.defer()
        check = await self.bot.db.get_guild_level_role(interaction.guild.id, role.id)
        if not check:
            await interaction.followup.send("追加されていないロールです")
            return
        await self.bot.db.delete_guild_level_role(interaction.guild.id, role.id)
        await interaction.followup.send("レベルロールを削除しました")

    @role_group.command(name="clear", description="レベルロールを全て削除します")
    async def level_role_remove(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.db.delete_all_guild_level_roles(interaction.guild.id)
        await interaction.followup.send("レベルロールを全て削除しました")

    @role_group.command(
        name="stack", description="レベルロールを複数保持するか設定します"
    )
    @app_commands.describe(value="設定する値")
    async def set_stack_level_roles(
        self, interaction: discord.Interaction, value: bool
    ):
        await interaction.response.defer()
        guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        if not guild_settings:
            await self.bot.db.create_guild_setting(interaction.guild.id)
            guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        min_exp, max_exp, _ = guild_settings
        await self.bot.db.update_guild_setting(
            interaction.guild.id, min_exp, max_exp, value
        )
        await interaction.followup.send("レベルロールの複数保持設定をしました")

    @exp_group.command(name="min", description="最小獲得経験値を設定します")
    @app_commands.describe(value="設定する値")
    async def set_min_exp(self, interaction: discord.Interaction, value: int):
        await interaction.response.defer()
        if value < 0:
            await interaction.followup.send("0以上で指定してください")
            return
        guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        if not guild_settings:
            await self.bot.db.create_guild_setting(interaction.guild.id)
            guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        _, max_exp, stack_level_roles = guild_settings
        await self.bot.db.update_guild_setting(
            interaction.guild.id, value, max_exp, stack_level_roles
        )
        await interaction.followup.send("最小獲得経験値を設定しました")

    @exp_group.command(name="max", description="最大獲得経験値を設定します")
    @app_commands.describe(value="設定する値")
    async def set_max_exp(self, interaction: discord.Interaction, value: int):
        await interaction.response.defer()
        if value < 0:
            await interaction.followup.send("0以上で指定してください")
            return
        guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        if not guild_settings:
            await self.bot.db.create_guild_setting(interaction.guild.id)
            guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        min_exp, _, stack_level_roles = guild_settings
        await self.bot.db.update_guild_setting(
            interaction.guild.id, min_exp, value, stack_level_roles
        )
        await interaction.followup.send("最大獲得経験値を設定しました")

    @exp_group.command(name="reset", description="経験値をリセットします")
    @app_commands.describe(user="リセットするメンバー、指定しない場合全員")
    async def reset_exp(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer()
        if user:
            await self.bot.db.delete_user_level_v1(user.id, interaction.guild.id)
            await interaction.followup.send("経験値をリセットしました")
            return
        await self.bot.db.delete_all_user_levels_v1(interaction.guild.id)
        await interaction.followup.send("全員の経験値をリセットしました")

    @app_commands.command(name="reset", description="サーバーの設定をリセットします")
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.db.delete_guild_setting(interaction.guild.id)
        await self.bot.db.create_guild_setting(interaction.guild.id)
        await interaction.followup.send("サーバーの設定をリセットしました")

    @app_commands.command(name="show", description="サーバーの設定を表示します")
    async def show(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_settings = await self.bot.db.get_guild_setting(interaction.guild.id)
        if not guild_settings:
            await interaction.followup.send("No Data")
            return
        min_exp, max_exp, stack_level_roles = guild_settings
        await interaction.followup.send(
            f"最小経験値: {min_exp}\n最大経験値: {max_exp}\nレベルロールの複数保持: {stack_level_roles}"
        )


async def setup(bot):
    await bot.add_cog(AdminSettingCommand(bot))
