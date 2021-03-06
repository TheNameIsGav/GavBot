import os
import asyncio
import discord
import random
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
    await trollConan()


async def trollConan():
    global amOnline
    loop = asyncio.get_running_loop()
    while True:
        await huntForConan()
        if(not amOnline):
            break
        randomInt = random.randint(2700,10800)
        print("Sleeping for {0} seconds".format(randomInt))
        await asyncio.sleep(randomInt)


usersToAnnoy = [
    210977628545351680, #conan
    214079671652843521, #jedi
    306948002483011584 #lemonite
]

async def huntForConan():
    print("Hunting for Conan")
    for guild in client.guilds:
        for channel in guild.voice_channels:
            voiceMapping = channel.voice_states
            for item in voiceMapping.keys():
                if item == 210977628545351680:
                #if item in usersToAnnoy:
                    user = await client.fetch_user(item)
                    print("Found {1} in {0}".format(channel.name, user))
                    vc = await channel.connect()
                    await vc.disconnect()

#conans id: 210977628545351680

@client.event
async def on_message(message):

    currGuild = message.guild
    currUser = message.author.id

    if message.author == client.user:
        return

    if message.content.startswith('$test'):
        user = await client.fetch_user(121406882865872901)
        await user.send("test")

    if message.content.startswith('$quit'):
        global amOnline
        amOnline = False
        
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1) 

client.run(TOKEN)