import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# 仮想通貨残高（ZeniTh coin）
user_balances = {}

@bot.event
async def on_ready():
    print(f"✅ ログイン完了：{bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ スラッシュコマンドを同期しました：{len(synced)}個")
    except Exception as e:
        print(f"エラー: {e}")

# /残高確認 コマンド
@bot.tree.command(name="残高確認", description="自分のZeniTh coin残高を確認します。")
async def check_balance(interaction: discord.Interaction):
    user_id = interaction.user.id
    balance = user_balances.get(user_id, 0)
    await interaction.response.send_message(
        f"{interaction.user.display_name}さんの残高は {balance} ZeniTh coin です！"
    )

# Bot起動
load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))