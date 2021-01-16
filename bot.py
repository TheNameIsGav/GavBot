import os

import asyncio
import discord
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
amOnline = False

@client.event
async def on_ready():
    global amOnline
    amOnline = True
    print('Logged in as {0.user}'.format(client))
    
@client.event
async def on_message(message):

    currGuild = message.guild
    currUser = message.author.id

    if message.author == client.user:
        return

    if message.content.startswith('$quit'):
        global amOnline
        amOnline = False
            
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1) 

    
        

    



client.run(TOKEN)