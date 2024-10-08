# SPDX-License-Identifier: CC-BY-NC-SA-4.0
# Author: Miriel (@mirielnet)

import discord
from discord import app_commands
from discord.ext import commands
import os
import importlib.util
import inspect


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help", description="すべてのスラッシュコマンドとその説明を表示します。"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ヘルプ",
            description="使用可能なスラッシュコマンド一覧",
            color=0x00FF00,
        )

        # ./commands フォルダ内の .py ファイルを対象にする
        commands_folder = "./commands"
        for file in os.listdir(commands_folder):
            if file.endswith(".py"):
                module_name = file[:-3]
                module_path = os.path.join(commands_folder, file)

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in vars(module).items():
                    # Cogクラスを見つける
                    if inspect.isclass(obj) and issubclass(obj, commands.Cog):
                        cog = obj(self.bot)
                        for command in cog.__cog_app_commands__:
                            embed.add_field(
                                name=f"/{command.name}",
                                value=command.description or "説明なし",
                                inline=False,
                            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
