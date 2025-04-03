import os
import discord
import logging
import logging.config
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from ArchivedCommands.crafting import *
from ArchivedCommands.secret_santa import *
from task import *
from chatgpt import *
from stats import *

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

#Change this line to change which guild to activate on
GUILD = None

async def syncCogs(guild=None):
    #await client.add_cog(Crafting(client), guild=guild)
    #await client.add_cog(SecretSanta(client), guild=guild)
    #await client.add_cog(TaskSession(client), guild=guild)
    await client.add_cog(TextGenerator(client))
    await client.add_cog(UserStats(client))
    #await client.add_cog(TaskSession(client))

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

    if(GUILD == None):
        await syncCogs()
    else:
        await syncCogs(guild=GUILD)
    synced = await client.tree.sync()
    Log(f"Synced {len(synced)} command(s).")
    Log("Client Ready", loggerName="main")
    amOnline = True

@client.event
async def close():
    Log("Closed Client", loggerName="main")
    Log("------------", loggerName="main")
    logging.shutdown()

client.run(TOKEN)