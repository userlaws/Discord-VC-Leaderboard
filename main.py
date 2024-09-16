import discord
from discord.ext import commands, tasks
from collections import defaultdict
import datetime
import requests
import time
import json
import os

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your webhook URL
webhook_url = 'your_webhook_url_here'
webhook_message_id = None
data_file = 'vc_times.json'

def load_vc_times():
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            for user_id, times in data.items():
                data[user_id] = {
                    "join_time": datetime.datetime.fromisoformat(times["join_time"]) if times["join_time"] else None,
                    "total_time": datetime.timedelta(seconds=times["total_time"]),
                    "muted_time": datetime.timedelta(seconds=times["muted_time"]),
                    "deafened_time": datetime.timedelta(seconds=times["deafened_time"]),
                    "muted_start": datetime.datetime.fromisoformat(times["muted_start"]) if times["muted_start"] else None,
                    "deafened_start": datetime.datetime.fromisoformat(times["deafened_start"]) if times["deafened_start"] else None,
                    "in_channel": times.get("in_channel", False)
                }
            return defaultdict(lambda: {"join_time": None, "total_time": datetime.timedelta(0), "muted_time": datetime.timedelta(0), "deafened_time": datetime.timedelta(0), "muted_start": None, "deafened_start": None, "in_channel": False}, data)
    return defaultdict(lambda: {"join_time": None, "total_time": datetime.timedelta(0), "muted_time": datetime.timedelta(0), "deafened_time": datetime.timedelta(0), "muted_start": None, "deafened_start": None, "in_channel": False})

def save_vc_times():
    with open(data_file, 'w') as f:
        serializable_data = {user_id: {
            "join_time": times["join_time"].isoformat() if times["join_time"] else None,
            "total_time": times["total_time"].total_seconds(),
            "muted_time": times["muted_time"].total_seconds(),
            "deafened_time": times["deafened_time"].total_seconds(),
            "muted_start": times["muted_start"].isoformat() if times["muted_start"] else None,
            "deafened_start": times["deafened_start"].isoformat() if times["deafened_start"] else None,
            "in_channel": times["in_channel"]
        } for user_id, times in vc_times.items()}
        json.dump(serializable_data, f)

vc_times = load_vc_times()

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    post_and_update_leaderboard.start()

@tasks.loop(seconds=6)
async def post_and_update_leaderboard():
    global webhook_message_id
    embed = discord.Embed(title="Voice Channel Leaderboard", color=discord.Color.gold())
    medal_emojis = ["🥇", "🥈", "🥉"]

    leaderboard_data = []
    for user_id, data in vc_times.items():
        if data["in_channel"] or data["total_time"] > datetime.timedelta(0):
            current_time_spent = data["total_time"]
            if data["join_time"] is not None and data["in_channel"]:
                current_time_spent += datetime.datetime.utcnow() - data["join_time"]
            leaderboard_data.append((user_id, current_time_spent, data))

    leaderboard_data.sort(key=lambda x: x[1], reverse=True)

    if not leaderboard_data:
        print("No data available for the leaderboard.")
        return

    first_user_avatar_url = None
    for idx, (user_id, total_time, data) in enumerate(leaderboard_data):
        user = bot.get_user(int(user_id))
        if user is None:
            continue

        time_spent = str(total_time).split('.')[0]

        status_icons = ""
        if data["muted_time"].total_seconds() > 0:
            status_icons += f"🔇 {str(data['muted_time']).split('.')[0]} "
        if data["deafened_time"].total_seconds() > 0:
            status_icons += f"🔈 {str(data['deafened_time']).split('.')[0]} "

        if idx == 0:
            first_user_avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            medal = medal_emojis[idx]
            embed.add_field(name=f"{idx + 1}. {user.name} {medal} {status_icons}", value=f"**{time_spent}**", inline=False)
        else:
            if idx < 3:
                medal = medal_emojis[idx]
                embed.add_field(name=f"{idx + 1}. {user.name} {medal} {status_icons}", value=f"**{time_spent}**", inline=False)
            else:
                embed.add_field(name=f"{idx + 1}. {user.name} {status_icons}", value=f"{time_spent}", inline=False)

    if first_user_avatar_url:
        embed.set_thumbnail(url=first_user_avatar_url)

    current_time = int(time.time())
    content = f"Last Updated: <t:{current_time}:R>"

    if webhook_message_id is None:
        webhook_data = {"username": "Leaderboard Bot", "content": content, "embeds": [embed.to_dict()]}
        response = requests.post(webhook_url, json=webhook_data)
        if response.status_code == 200:
            webhook_message_id = response.json().get("id")
            print("Leaderboard posted successfully!")
        else:
            print(f"Failed to send the leaderboard. Status code: {response.status_code} - {response.text}")
    else:
        webhook_data = {"content": content, "embeds": [embed.to_dict()]}
        edit_url = f"{webhook_url}/messages/{webhook_message_id}"
        response = requests.patch(edit_url, json=webhook_data)
        if response.status_code in [200, 204]:
            print("Leaderboard updated successfully!")
        else:
            print(f"Failed to update webhook message: {response.status_code} - {response.text}")

@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    if user_id not in vc_times:
        vc_times[user_id] = {"join_time": None, "total_time": datetime.timedelta(0), "muted_time": datetime.timedelta(0), "deafened_time": datetime.timedelta(0), "muted_start": None, "deafened_start": None, "in_channel": False}

    user_data = vc_times[user_id]

    if before.channel is None and after.channel is not None:
        user_data["join_time"] = datetime.datetime.utcnow()
        user_data["in_channel"] = True
    elif before.channel is not None and after.channel is None:
        if user_data["join_time"]:
            time_spent = datetime.datetime.utcnow() - user_data["join_time"]
            user_data["total_time"] += time_spent
            user_data["join_time"] = None
        user_data["in_channel"] = False

    if after.self_mute and not user_data["muted_start"]:
        user_data["muted_start"] = datetime.datetime.utcnow()
    elif not after.self_mute and user_data["muted_start"]:
        user_data["muted_time"] += datetime.datetime.utcnow() - user_data["muted_start"]
        user_data["muted_start"] = None

    if after.self_deaf and not user_data["deafened_start"]:
        user_data["deafened_start"] = datetime.datetime.utcnow()
    elif not after.self_deaf and user_data["deafened_start"]:
        user_data["deafened_time"] += datetime.datetime.utcnow() - user_data["deafened_start"]
        user_data["deafened_start"] = None

    save_vc_times()

# Replace with your bot token
bot.run('your_bot_token_here')
