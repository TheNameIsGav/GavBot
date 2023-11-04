import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from crafting import *
from secret_santa import *

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
GUILD = TEST_GUILD

async def syncCogs(guild=None):
    await client.add_cog(Crafting(client), guild=guild)
    await client.add_cog(SecretSanta(client), guild=guild)

@client.event
async def on_ready():
    global amOnline
    amOnline = True
    await syncCogs(guild=GUILD)
    await client.tree.sync(guild=GUILD)
    print('Logged in as {0.user}'.format(client))

client.run(TOKEN)