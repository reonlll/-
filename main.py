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

@bot.tree.command(name="送金", description="ZeniTh coinを他のユーザーに送金します。")
@app_commands.describe(member="送金相手", amount="送る金額（整数）")
async def send_zenith(interaction: discord.Interaction, member: discord.Member, amount: int):
    sender_id = interaction.user.id
    receiver_id = member.id

    if amount <= 0:
        await interaction.response.send_message("送金額は1以上にしてください。", ephemeral=True)
        return

    sender_balance = user_balances.get(sender_id, 0)

    if sender_balance < amount:
        await interaction.response.send_message("残高が足りません。", ephemeral=True)
        return

    # 残高の更新
    user_balances[sender_id] = sender_balance - amount
    user_balances[receiver_id] = user_balances.get(receiver_id, 0) + amount

    await interaction.response.send_message(
        f"{member.display_name} さんに {amount} ZeniTh coin を送金しました！",
        ephemeral=True
    )
    
    @bot.tree.command(name="付与", description="管理者用：指定ユーザーにZeniTh coinを付与します。")
    @app_commands.describe(member="付与する相手", amount="付与するZeniTh coinの金額")
async def grant_zenith(interaction: discord.Interaction, member: discord.Member, amount: int):
    # 管理者チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("付与額は1以上にしてください。", ephemeral=True)
        return

    user_balances[member.id] = user_balances.get(member.id, 0) + amount

    await interaction.response.send_message(
        f"{member.display_name} さんに {amount} ZeniTh coin を付与しました！",
        ephemeral=True
    )
    
    @bot.tree.command(name="金額確認", description="管理者用：指定ユーザーのZeniTh coin残高を確認します。")
@app_commands.describe(member="残高を確認したいユーザー")
async def check_other_balance(interaction: discord.Interaction, member: discord.Member):
    # 管理者権限チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return

    balance = user_balances.get(member.id, 0)
    await interaction.response.send_message(
        f"{member.display_name} さんの残高は {balance} ZeniTh coin です。",
        ephemeral=True
    )
    
    @bot.tree.command(name="ロール送金", description="管理者用：指定ロールの全メンバーにZeniTh coinを一括送金します。")
@app_commands.describe(role="対象ロール", amount="一人あたりの送金額（整数）")
async def send_to_role(interaction: discord.Interaction, role: discord.Role, amount: int):
    # 管理者チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("送金額は1以上にしてください。", ephemeral=True)
        return

    # 対象メンバーの取得
    recipients = [member for member in role.members if not member.bot]

    if not recipients:
        await interaction.response.send_message("そのロールにはBot以外のメンバーがいません。", ephemeral=True)
        return

    for member in recipients:
        user_balances[member.id] = user_balances.get(member.id, 0) + amount

    await interaction.response.send_message(
        f"{role.name} ロールの {len(recipients)} 人に、{amount} ZeniTh coin を送金しました！",
        ephemeral=True
    )
    
    @bot.tree.command(name="金額ランキング", description="管理者用：ZeniTh coinの残高ランキングを表示します。")
async def zenith_ranking(interaction: discord.Interaction):
    # 管理者チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return

    # ギルドのメンバー情報を使ってランキング作成（Bot除外）
    members = [member for member in interaction.guild.members if not member.bot]
    balances = [(member, user_balances.get(member.id, 0)) for member in members]
    sorted_balances = sorted(balances, key=lambda x: x[1], reverse=True)

    if not sorted_balances:
        await interaction.response.send_message("ランキングを表示できるユーザーがいません。", ephemeral=True)
        return

    # 上位10人まで表示
    top_list = sorted_balances[:10]
    rank_message = "🏆 **ZeniTh coin ランキング** 🏆\n\n"
    for i, (member, balance) in enumerate(top_list, start=1):
        rank_message += f"{i}. {member.display_name}：{balance} ZeniTh coin\n"

    await interaction.response.send_message(rank_message, ephemeral=True)

@bot.tree.command(name="残高減少", description="管理者用：指定ユーザーのZeniTh coinを減らします。")
@app_commands.describe(member="残高を減らす対象のユーザー", amount="減らすZeniTh coinの金額")
async def decrease_balance(interaction: discord.Interaction, member: discord.Member, amount: int):
    # 管理者チェック
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("減少額は1以上にしてください。", ephemeral=True)
        return

    current_balance = user_balances.get(member.id, 0)
    new_balance = max(0, current_balance - amount)
    user_balances[member.id] = new_balance

    await interaction.response.send_message(
        f"{member.display_name} さんの残高を {amount} ZeniTh coin 減らしました。\n現在の残高：{new_balance} ZeniTh coin",
        ephemeral=True
    )

# Bot起動
load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))