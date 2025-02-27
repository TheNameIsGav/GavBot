import os
import discord
import logging
import logging.config
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from crafting import *
from secret_santa import *
from task import *
from chatgpt import *

load_dotenv()

intents = discord.Intents.all()
intents.members = True
intents.messages = True
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

@client.event
async def on_ready():
    global amOnline
    amOnline = True
    if(GUILD == None):
        await syncCogs()
    else:
        await syncCogs(guild=GUILD)
    synced = await client.tree.sync()
    Log(f"Synced {len(synced)} command(s).")
    
    date = datetime.datetime.today().strftime("%Y-%m-%d")
    target_path = f'{os.path.join(os.getcwd(), "Logs", f"{date}")}'
    logging.basicConfig(filename=target_path, filemode="a", encoding='utf-8', level=logging.DEBUG)
    Log("Client Ready", loggerName="main")

@client.event
async def close():
    Log("Closed Client", loggerName="main")
    Log("------------", loggerName="main")

client.run(TOKEN)