# SPDX-License-Identifier: CC-BY-NC-SA-4.0
# Author: Miriel (@mirielnet)

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import glob
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
import aiofiles
from version import BOT_VERSION

app = FastAPI()

# .envファイルからトークンを読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# インテントの設定
intents = discord.Intents.default()
intents.message_content = True

# ボットのインスタンスを作成
bot = commands.Bot(command_prefix='!', intents=intents)

# コマンドのロード
async def load_commands():
    for filename in glob.glob('./commands/*.py'):
        if filename.endswith('.py') and not filename.endswith('__init__.py'):
            try:
                await bot.load_extension(f'commands.{os.path.basename(filename)[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

# グローバルスラッシュコマンドの登録
@bot.event
async def on_ready():
    # コマンドの同期と登録
    await bot.tree.sync()
    
    # グローバルコマンドの登録確認メッセージ
    print("グローバルコマンドが正常に登録されました。")

    # サーバー数を取得してステータスを設定
    server_count = len(bot.guilds)
    activity = discord.Game(name=f'{BOT_VERSION} / {server_count} servers')
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'{bot.user}がDiscordに接続され、{server_count}サーバーに参加しています。')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        print(f'Error in command {ctx.command}: {error}')

# index.htmlを表示するエンドポイント
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    async with aiofiles.open("static/index.html", mode="r", encoding="utf-8") as f:
        template = Template(await f.read())
    content = template.render(
        server_count=len(bot.guilds),
        servers=bot.guilds
    )
    return HTMLResponse(content=content)

# ボットの起動
async def start_bot():
    await load_commands()
    await bot.start(TOKEN)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
