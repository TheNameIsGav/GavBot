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
    #await trollConan()

"""
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
    210977628545351680 #conan
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
"""

async def WriteAddress(message):
    currUser = message.author
    messageText = message.content[6:]
    with open(".add", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(":")
            if int(line[0]) == message.author.id:
                await message.author.send("You appear to have already written your address as " + line[1] + "\nUse the $remove command if this is incorrect")
                return

    with open(".add", "a") as file:
        file.write(str(currUser.id) + ":" + messageText + "\n")
    await message.author.send("Wrote Address as: " + messageText + "\nIf this is incorrect, please use the $remove command")

async def RemoveAddress(message):
    userID = message.author.id
    tempString = ""
    with open(".add", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(":")
            if(int(line[0]) != userID):
                tempString += line[0] + ":" + line[1]
    
    with open(".add", "w") as file:
        file.write(tempString)

    await message.author.send("Removed address successfully")

async def DistributeAddresses(messages):

    userDict = {}
    with open(".add", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(":")
            userDict[line[0]] = line[1]

    keys = list(userDict.keys())
    random.shuffle(keys)

    firstKey = keys[0]
    prevKey = keys[0]
    for i in range(1, len(keys)):
        currUser = keys[i]
        user = await client.fetch_user(currUser)
        prevUser = await client.fetch_user(prevKey)
        await user.send("You got: " + prevUser.name + " who lives at " + userDict[prevKey])
        with open ("WishLists/" + prevUser.name + ".wsh", "r") as file:
            tmp = ""
            for line in file.readlines():
                tmp += line + '\n'
            await user.send("Their wishlist is " + tmp)
        prevKey = currUser

    await (await client.fetch_user(firstKey)).send("You got: " + (await client.fetch_user(keys[-1])).name + " who lives at " + userDict[keys[-1]])
    with open ("WishLists/" + (await client.fetch_user(keys[-1])).name + ".wsh", "r") as file:
            tmp = ""
            for line in file.readlines():
                tmp += line + '\n'
            await (await client.fetch_user(firstKey)).send("Their wishlist is " + tmp)

async def checkUsers(message):
    with open(".add", "r") as file:
        lines = file.readlines()
        tmp = ""
        for line in lines:
            line = line.split(":")
            tmp += (await client.fetch_user(line[0])).name + '\n'
        
        await message.channel.send("The following users have signed up: \n" + tmp)

async def AddToWishList(message):
    with open("Wishlists/" + message.author.name + ".wsh", "a") as file:
        file.write('\n' + message.content[10:])
    await message.author.send("Added " + message.content[10:] + " to your wishlist")

async def CheckWishList(message):
    with open("Wishlists/" + message.author.name + ".wsh", "r") as file:
        lines = file.readlines()
        tmp = ""
        for line in lines:
            tmp += line + '\n'
    await message.author.send("Your wishlist is: " + tmp)

@client.event
async def on_message(message):

    currGuild = message.guild
    currUser = message.author.id

    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        await message.channel.send("Hello there! You called?")

    if message.content.startswith("$enter"):
        await WriteAddress(message)

    if message.content.startswith("$remove"):
        await RemoveAddress(message)

    if message.content.startswith("$run") and message.author.id == 121406882865872901:
        await DistributeAddresses(message)

    if message.content.startswith('$help'):
        tmp = """```
$enter - Used to enter your address in the format of <Street Address City, State Zipcode, Perferred Delivery Name>. Example: $enter 1111 Street Waco, Texas 78787, Gav
$remove - Used to remove your name and address from the pool. 
$check - Used to check current users signed up for Secret Santa. Example: $check
$wishlist - Used to add a single item to your wishlist. Example: $wishlist Cotton Candy
$mywishlist - Used to check your wishlist. Example: $mywishlist
$fuck - You'll see```"""
        await message.channel.send(tmp)

    if message.content.startswith('$check'):
        await checkUsers(message)

    if message.content.startswith('$wishlist'):
        await AddToWishList(message)

    if message.content.startswith('$mywishlist'):
        await CheckWishList(message)

    if message.content.startswith('$fuck'):
        await message.channel.send("Fuck off")

    if message.content.startswith ('$hohoho'):
        await message.channel.send("||ho ho ho||")

    if message.content.startswith('$quit') and message.author.id == 121406882865872901:
        global amOnline
        amOnline = False
        
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1) 

client.run(TOKEN)