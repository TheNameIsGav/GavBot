import os

import asyncio
import discord
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
amOnline = False

def getUserID(content):
    firstCarrot = content.index('<')
    secondCarrot = content.index('>')
    return int(content[firstCarrot+3:secondCarrot])

@client.event
async def on_ready():
    global amOnline
    amOnline = True
    print('Logged in as {0.user}'.format(client))
    
@client.event
async def on_message(message):

    currGuild = message.guild

    if message.author == client.user:
        return

    if message.content.startswith('$quit'):
        global amOnline
        amOnline = False
            
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1) 

    if message.author.id == 159985870458322944 or message.content.startswith('$turboCum'):
        
        userID = getUserID(message.content)
        member = currGuild.get_member(userID)
        



client.run(TOKEN)