import os
import discord
import logging
import logging.config
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from dnd_utils import *
from ArchivedCommands.secret_santa import *
from task import *
from chatgpt import *
from stats import *
from chores import *
from suggestions_writer import *

load_dotenv()

intents = discord.Intents.all()
intents.members = True
intents.messages = True
intents.message_content=True
amOnline = False
client = commands.Bot(command_prefix="$", intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_GUILD = discord.Object(os.getenv('DISCORD_TEST_GUILD'))
LIVE_GUILD = discord.Object(os.getenv('DISCORD_LIVE_GUILD'))
MY_GUILD = discord.Object(os.getenv('DISCORD_MAIN_GUILD'))

#Change this line to change which guild to activate on
GUILD = None
COGS = {}

async def syncCogs(guild=None):
    #await client.add_cog(Crafting(client), guild=guild)
    #await client.add_cog(SecretSanta(client), guild=guild)
    #await client.add_cog(TaskSession(client), guild=guild)
    text_cog = TextGenerator(client)
    await client.add_cog(text_cog)
    COGS["text_cog"] = text_cog

    user_cog = UserStats(client)
    await client.add_cog(user_cog)
    COGS["user_cog"] = user_cog

    dnd_cog = DNDUtils(client)
    await client.add_cog(dnd_cog)
    COGS["dnd_cog"] = dnd_cog

    #task_cog = TaskSession(client)
    #await client.add_cog(TaskSession(client))
    #COGS.append(task_cog)

    #chores_cog = ChoreDistributor(client)
    #await client.add_cog(chores_cog)
    #COGS["chores_cog"] = chores_cog

    synced = await client.tree.sync()
    Log(f"Synced {len(synced)} command(s).")

    #Always sync exclusively to MY server
    suggestions_cog = GitHubFileEditor(client)
    await client.add_cog(suggestions_cog)
    COGS["suggestions_cog"] = suggestions_cog

    client.tree.copy_global_to(guild=MY_GUILD)
    synced = await client.tree.sync(guild=MY_GUILD)
    Log(f"Synced {len(synced)} command(s).")

@client.event
async def on_ready():
    global amOnline

    date = datetime.datetime.today().strftime("%Y-%m-%d")
    path = os.getenv('CUSTOMPATH')
    target_path = f'{os.path.join(path, f"{date}.log")}'
    if(not os.path.exists(target_path)):
        f = open(target_path, "w")
        f.close()
    logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(target_path), logging.StreamHandler()],
        )
    
    await syncCogs()

    # if not hasattr(client, 'weekly_task_started'):
    #     client.weekly_task_started = True
    #     weekly_tasks = [COGS["chores_cog"].distribute_chores]
    #     asyncio.create_task(run_weekly_tasks_persisted(weekly_tasks, weekday=6))

    
    Log("Client Ready", loggerName="main")
    amOnline = True

@client.event
async def close():
    Log("Closed Client", loggerName="main")
    Log("------------", loggerName="main")
    logging.shutdown()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("🚫 You are not the bot owner and cannot use this command.")
    else:
        # Handle other errors or re-raise them if unhandled
        await ctx.send("Something raised a command error")

#region Timer

import asyncio
import datetime
import json
import os
from typing import Callable

SCHEDULER_FILE = "next_weekly_run.json"

def save_next_run_time(dt: datetime.datetime):
    with open(SCHEDULER_FILE, "w") as f:
        json.dump({"next_run": dt.isoformat()}, f)

def load_next_run_time(default_weekday: int = 6) -> datetime.datetime:
    """
    Load the next run time from file or calculate it for the next default_weekday (Sunday = 6).
    """
    if os.path.exists(SCHEDULER_FILE):
        try:
            with open(SCHEDULER_FILE, "r") as f:
                data = json.load(f)
                return datetime.datetime.fromisoformat(data["next_run"])
        except Exception as e:
            print(f"⚠️ Failed to load saved time: {e}")

    now = datetime.datetime.now()
    days_ahead = (default_weekday - now.weekday()) % 7
    if days_ahead == 0 and now.hour >= 0:
        days_ahead = 7  # it's already Sunday today after midnight, so wait until next week

    return (now + datetime.timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)

async def run_weekly_tasks_persisted(task_list: list[Callable], weekday: int = 6):
    """
    Run tasks weekly at midnight on the given weekday (default Sunday = 6), and persist schedule across restarts.
    """
    next_run = load_next_run_time(default_weekday=weekday)

    while True:
        now = datetime.datetime.now()
        seconds_until_next_run = (next_run - now).total_seconds()
        if seconds_until_next_run > 0:
            print(f"🕰 Sleeping for {int(seconds_until_next_run)} seconds until next weekly run: {next_run}")
            await asyncio.sleep(seconds_until_next_run)

        print(f"[{datetime.datetime.now()}] 📅 Running weekly midnight tasks...")
        for task in task_list:
            try:
                result = task()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"⚠️ Task {task.__name__} failed: {e}")

        # Schedule next week's run and persist it
        next_run = next_run + datetime.timedelta(weeks=1)
        save_next_run_time(next_run)

        await asyncio.sleep(1)


#endregion 

client.run(TOKEN)