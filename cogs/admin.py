import discord
from discord import app_commands
from discord.ext import commands
from main import DiscordLevelBot


class EXPResetConfirm(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__()
        self.value = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    @discord.ui.button(label="リセットする", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="リセットしています...", view=None
        )
        self.value = True
        self.stop()

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="キャンセルしました", view=None)
        self.value = False
        self.stop()


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
        view = EXPResetConfirm(interaction.user)
        await interaction.response.send_message(
            f"{user.display_name if user else '全員'}の経験値をリセットしますか？",
            view=view,
        )
        await view.wait()

        if view.value:
            if user:
                await self.bot.db.delete_user_level_total(user.id, interaction.guild.id)
                await interaction.followup.send(
                    f"{user.display_name}の経験値をリセットしました"
                )
            else:
                await self.bot.db.delete_all_user_levels(interaction.guild.id)
                await interaction.followup.send("全員の経験値をリセットしました")

    @exp_group.command(name="add", description="経験値を追加します")
    @app_commands.describe(user="追加するメンバー")
    @app_commands.describe(channel="追加するチャンネル")
    @app_commands.describe(value="追加する値")
    async def add_exp(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        channel: discord.abc.GuildChannel,
        value: int,
    ):
        await interaction.response.defer()
        if value < 1:
            await interaction.followup.send("1以上で指定してください")
            return
        await self.bot.db.add_user_level(
            user.id, interaction.guild.id, channel.id, value
        )
        await interaction.followup.send(
            f"{user.display_name}に{value}経験値追加しました"
        )

    @exp_group.command(name="remove", description="経験値を減らします")
    @app_commands.describe(user="減らすメンバー")
    @app_commands.describe(channel="減らすチャンネル")
    @app_commands.describe(value="減らす値")
    async def remove_exp(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        channel: discord.abc.GuildChannel,
        value: int,
    ):
        await interaction.response.defer()
        if value < 1:
            await interaction.followup.send("1以上で指定してください")
            return
        exp = await self.bot.db.get_user_level(
            user.id, interaction.guild.id, channel.id
        )
        if exp < value:
            value = exp
        await self.bot.db.remove_user_level_exp(
            user.id, interaction.guild.id, interaction.channel.id, value
        )
        await interaction.followup.send(
            f"{user.display_name}から{value}経験値減らしました"
        )

    @app_commands.command(name="reset", description="サーバーの設定をリセットします")
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.db.delete_guild_setting(interaction.guild.id)
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
            f"最小経験値: {min_exp}\n最大経験値: {max_exp}\nレベルロールの複数保持: {'はい' if stack_level_roles else 'いいえ'}"
        )


async def setup(bot):
    await bot.add_cog(AdminSettingCommand(bot))
