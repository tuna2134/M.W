# SPDX-License-Identifier: CC-BY-NC-SA-4.0
# Author: Miriel (@mirielnet)

import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

# SQLite データベース設定
DB_PATH = "./db/autorole.db"


def initialize_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS autoroles (
                server_id INTEGER PRIMARY KEY,
                role_ids TEXT
            )
        """
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"データベースの初期化中にエラーが発生しました: {e}")
    finally:
        conn.close()


def get_autoroles(server_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role_ids FROM autoroles WHERE server_id = ?", (server_id,)
        )
        result = cursor.fetchone()
        if result:
            return result[0].split(",")
    except sqlite3.Error as e:
        print(f"自動ロールの取得中にエラーが発生しました: {e}")
        return []
    finally:
        conn.close()


def set_autoroles(server_id, role_ids):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO autoroles (server_id, role_ids)
            VALUES (?, ?)
        """,
            (server_id, ",".join(role_ids)),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"自動ロールの設定中にエラーが発生しました: {e}")
    finally:
        conn.close()


def remove_autoroles(server_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM autoroles WHERE server_id = ?", (server_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"自動ロールの削除中にエラーが発生しました: {e}")
    finally:
        conn.close()


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        initialize_db()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role_ids = get_autoroles(member.guild.id)
            roles = [
                member.guild.get_role(int(role_id))
                for role_id in role_ids
                if member.guild.get_role(int(role_id))
            ]
            if roles:
                await member.add_roles(*roles)
                print(
                    f"{member.display_name} に自動ロールを付与しました: {', '.join([role.name for role in roles])}"
                )
            else:
                print(f"{member.display_name} に付与するロールが設定されていません。")
        except Exception as e:
            print(f"メンバー入室時のエラー: {e}")

    @app_commands.command(name="autorole_set", description="自動ロールを設定します。")
    @app_commands.describe(roles="自動付与するロールを選択してください。")
    @app_commands.checks.has_permissions(administrator=True)
    async def autorole_set(self, interaction: discord.Interaction, roles: discord.Role):
        await interaction.response.defer()
        try:
            role_ids = (
                [str(roles.id)]
                if isinstance(roles, discord.Role)
                else [str(role.id) for role in roles]
            )
            set_autoroles(interaction.guild.id, role_ids)
            await interaction.followup.send(
                f"自動ロールを設定しました: {', '.join([interaction.guild.get_role(int(role_id)).name for role_id in role_ids])}"
            )
        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {e}")

    @app_commands.command(
        name="autorole_update", description="自動ロールを変更します。"
    )
    @app_commands.describe(roles="新しい自動付与するロールを選択してください。")
    @app_commands.checks.has_permissions(administrator=True)
    async def autorole_update(
        self, interaction: discord.Interaction, roles: discord.Role
    ):
        await interaction.response.defer()
        try:
            role_ids = (
                [str(roles.id)]
                if isinstance(roles, discord.Role)
                else [str(role.id) for role in roles]
            )
            set_autoroles(interaction.guild.id, role_ids)
            await interaction.followup.send(
                f"自動ロールを変更しました: {', '.join([interaction.guild.get_role(int(role_id)).name for role_id in role_ids])}"
            )
        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {e}")

    @app_commands.command(
        name="autorole_remove", description="自動ロールの設定を解除します。"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def autorole_remove(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            remove_autoroles(interaction.guild.id)
            await interaction.followup.send("自動ロールの設定を解除しました。")
        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {e}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("このコマンドを実行するには管理者権限が必要です。")
        else:
            await ctx.send(f"エラーが発生しました: {error}")


async def setup(bot):
    await bot.add_cog(AutoRole(bot))
