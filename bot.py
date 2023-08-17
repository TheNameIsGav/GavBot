import os
import asyncio
from typing import Any, List, Optional, Union
import discord
from discord.components import SelectOption
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.ext import commands
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji
from discord.utils import MISSING
from dotenv import load_dotenv
import random
from enum import Enum

load_dotenv()

intents = discord.Intents.all()
intents.messages = True
amOnline = False
client = commands.Bot(command_prefix="$", intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')
musicPath = os.getcwd() + "\Music"
activeSessions = {}

class PlayStates(Enum):
    Playing = 0 #Currently playing audio
    Paused = 1 #Not playing audio, still in voice channel
    Stopped = 2 #not playing audio and not in voice channel

class Genre(Enum):
    Battle = 0
    Tavern = 1
    Adventuring = 2
    Boss = 3

class PlaySessionView(discord.ui.View):
    genre:Genre = Genre.Adventuring
    current_track = None
    should_loop = None
    voice_channel = None
    voice_client:discord.VoiceClient = None
    interaction:discord.Interaction = None
    embed = None
    playState:PlayStates = PlayStates.Stopped
    songQueue:[str] = []
    
    battleButton = None
    adventuringButton = None
    tavernButton = None
    bossButton = None    

    playPauseButton = None
    loopButton = None

    volumeUpButton = None
    volumeDownButton = None
    
    skipFowardButton = None
    skipBackwardsButton = None

    async def playSong(self):
        if(self.voice_client.is_playing):
            self.voice_client.stop()

        sound = random.choice(os.listdir(musicPath + "\\" + self.genre.name))
        file = os.path.join(musicPath, self.genre.name, sound)
        print(file)
        self.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=file))
        self.embed = discord.Embed(title=f"{self.genre.name}", description=f"{sound}", color=0xffffff)

        self.playPauseButton.style = discord.ButtonStyle.success
        self.playPauseButton.label = "⏸"
        await self.interaction.edit_original_response(embed=self.embed, view=self)
    
    def __init__(self, interaction:discord.Interaction):
        super().__init__(timeout=None)
        self.interaction = interaction

        self.battleButton = BattleButton(self)
        self.add_item(self.battleButton)

        self.adventuringButton = AdventuringButton(self)
        self.add_item(self.adventuringButton)

        self.tavernButton = TavernButton(self)
        self.add_item(self.tavernButton)

        self.bossButton = BossButton(self)
        self.add_item(self.bossButton)

        self.volumeUpButton = VolumeUpButton(self)
        self.add_item(self.volumeUpButton)

        self.playPauseButton = PlayPauseButton(self)
        self.add_item(self.playPauseButton)

        self.volumeDownButton = VolumeDownButton(self)
        self.add_item(self.volumeDownButton)

        self.skipBackwardsButton = SkipBackwardsButton(self)
        self.add_item(self.skipBackwardsButton)

        self.loopButton = LoopButton(self)
        self.add_item(self.loopButton)

        self.skipFowardButton = SkipFowardButton(self)
        self.add_item(self.skipFowardButton)

    async def startup(self):
        print(f"Starting new play session for guild: {self.interaction.guild.name}")
        voice_channel = self.interaction.user.voice.channel
        if(voice_channel == None): 
            await self.interaction.response.send_message("User is not connected to a voice channel")
            return
        
        activeSessions[self.interaction.guild_id] = self
        self.voice_client = await voice_channel.connect()

        #self.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="E:\GavBot\Music\Battle\\battle.mp3"))

        self.embed = discord.Embed(title = "Not playing", description="not playing", color=0xffffff)
        await self.interaction.response.send_message(embed=self.embed, view=self)
        self.playState = PlayStates.Paused

    async def playPauseButtonPressed(self):
        print("Play / Pause Button Pressed")
        if(self.voice_client.is_playing()):
            self.voice_client.pause()
            self.playPauseButton.style = discord.ButtonStyle.red
            self.playPauseButton.label = "⏵"
        elif(self.voice_client.is_paused()):
            self.voice_client.resume()
            self.playPauseButton.style = discord.ButtonStyle.success
            self.playPauseButton.label = "⏸"
        else:
            await self.playSong()
            self.playPauseButton.style = discord.ButtonStyle.success
            self.playPauseButton.label = "⏸"

        await self.interaction.edit_original_response(embed=self.embed, view=self)

    async def stopPlaying(self):
        print("Stopping playback")
        if(self.voice_client.is_connected()):
            await self.voice_client.disconnect()
            await self.interaction.delete_original_response()
            activeSessions.pop(self.interaction.guild_id)

    async def skipFoward(self): #TODO
        if(self.voice_client.is_playing()):
            self.voice_client.stop()

    async def skipBackwards(self): #TODO
        pass

    async def volumeUp(self): #TODO
        pass

    async def volumeDown(self): #TODO
        pass

    async def loop(self): #TODO
        pass

    async def changeGenre(self, value:Genre):
        self.genre = value

        self.battleButton.disabled = False
        self.battleButton.style = discord.ButtonStyle.gray

        self.adventuringButton.disabled = False
        self.adventuringButton.style = discord.ButtonStyle.gray

        self.bossButton.disabled = False
        self.bossButton.style = discord.ButtonStyle.gray

        self.tavernButton.disabled = False
        self.tavernButton.style = discord.ButtonStyle.gray
        match(value):
            case Genre.Battle:
                self.battleButton.disabled = True
                self.battleButton.style = discord.ButtonStyle.green
                pass
            case Genre.Adventuring:
                self.adventuringButton.disabled = True
                self.adventuringButton.style = discord.ButtonStyle.green
                pass
            case Genre.Tavern:
                self.tavernButton.disabled = True
                self.tavernButton.style = discord.ButtonStyle.green
                pass
            case Genre.Boss:
                self.bossButton.disabled = True
                self.bossButton.style = discord.ButtonStyle.green
                pass
        await self.playSong()
        pass

class PlayPauseButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.success, label="⏸", row=1)
        self.parent = parent

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        self.parent.playPauseButtonPressed()

class SkipFowardButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="⏭", row=2)
        self.parent = parent

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await self.parent.skipFoward()
        return await super().callback(interaction)

class SkipBackwardsButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="⏮", row=2)
        self.parent = parent

class LoopButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="↻",row=2)
        self.parent = parent

class VolumeUpButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="↑", row=1)
        self.parent = parent

class VolumeDownButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="↓", row=1)
        self.parent = parent

class BattleButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Battle", row=0)
        self.parent = parent

    async def callback(self, interaction) -> Any:
        await interaction.response.defer()
        await self.parent.changeGenre(Genre.Battle)

class TavernButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Tavern", row=0)
        self.parent = parent

    async def callback(self, interaction) -> Any:
        await interaction.response.defer()
        await self.parent.changeGenre(Genre.Tavern)

class AdventuringButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Adventuring", row=0)
        self.parent = parent

    async def callback(self, interaction) -> Any:
        await interaction.response.defer()
        await self.parent.changeGenre(Genre.Adventuring)

class BossButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Boss", row=0)
        self.parent = parent

    async def callback(self, interaction) -> Any:
        await interaction.response.defer()
        await self.parent.changeGenre(Genre.Boss)

@client.tree.command(name="play", description="plays music", guild=discord.Object(574438245505433640))
async def play(interaction: discord.Interaction):
    playsession = PlaySessionView(interaction)
    await playsession.startup()
    pass

@client.event
async def on_ready():
    global amOnline
    amOnline = True
    await client.tree.sync(guild=discord.Object(id=574438245505433640))
    #await client.tree.sync(guild=discord.Object(id=732703322930151760))
    print('Logged in as {0.user}'.format(client))

client.run(TOKEN)



"""
class MyHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        await channel.send("Hello!")

client.help_command = MyHelp()


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

async def CheckAddress(message):
    userID = message.author.id
    with open(".add", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(":")
            if(int(line[0]) == userID):
                await message.author.send(f"Address: {line[1]}")

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

async def CalculateDamage(message):
    x = int(message.content[4:])
    if(x == 1 or x == 2):
        await message.channel.send(1)
    else:
        await message.channel.send(math.ceil(1 + 1.91*(0.1 * (x**2))))

async def LocalSecretSanta(message):
    ids = [326781002175479810, 121406882865872901, 218080098341879809, 361622974232526848,
    331139792949477376, 623657140850130947, 114893373814341639, 239250141519806464, 227540507004239872]
    for id in ids:
        user = await client.fetch_user(id)
        #await user.send_friend_request()
        try:
            await user.send("Hopefully the last one I hate coding someone help me. Please say something in the group chat saying you got this message. ")
        except discord.Forbidden: 
            print(f"{id} was forbidden")
        

runningSessions = {}
async def SetupSession(message):
    dmID = message.author.id
    dmUser = message.author

    if(runningSessions.get(dmID) == None):
        IDs = message.content.split(" ")[1:] #The first name is the command
        assembledSession = []
        for id in IDs:
            id = id.replace("@", "")
            id = id.replace(">", "")
            id = id.replace("<", "")
            assembledSession.append(int(id))

        assembledSession.insert(0, dmID)

        session = (message.channel, dmID, assembledSession)

        for id in assembledSession:
            print(id)
            user = await client.fetch_user(id)
            print(user)
            await user.send("You have been added to " + dmUser.name + "'s DIE session for autonomously X'ing a topic!")

        runningSessions[dmID] = session
    else:
        await message.channel.send("It would appear that you already have a session in progress. Please end that session")

async def StopSession(message):
    session = runningSessions.pop(message.author.id)
    if(session == None):
        await message.channel.send('Couldn\'t find your session')
    else:
        await message.channel.send("Removed your session")

async def CheckSessions(message):
    formattedString = ""
    for session in runningSessions.values():
        dmUser = await client.fetch_user(session[1])
        participants = []
        for user in session[2]:
            participants.append((await client.fetch_user(user)).name)

        formattedString = formattedString + "\n A Session run by {0} with {1} as players".format(dmUser, participants)
    
    if(formattedString == ""):
        formattedString = "No active sessions"

    await message.channel.send(formattedString)

async def Alert(message):
    for session in runningSessions.values():
        if(message.author.id in session[2]):
            await session[0].send("@everyone Someone X'ed")

async def SendCharacters(message):
    user = await client.fetch_user(121406882865872901) #me
    await user.send(file=discord.File(r'E:\DnD\DIE\\The Fook.pdf'))

    user = await client.fetch_user(227610442309042176) #alan
    await user.send(file=discord.File(r'E:\DnD\DIE\\Godbinder.pdf'))

    user = await client.fetch_user(286921649364795395) #jason
    await user.send(file=discord.File(r'E:\DnD\DIE\\Emotion Knight.pdf'))

    user = await client.fetch_user(234806958882816001) #chris
    await user.send(file=discord.File(r'E:\DnD\DIE\\Dictator.pdf'))

    user = await client.fetch_user(420426512852844544) #kat
    await user.send(file=discord.File(r'E:\DnD\DIE\\NEO.pdf'))

    user = await client.fetch_user(626970737009360896) #maggie
    await user.send(file=discord.File(r'E:\DnD\DIE\\NEO.pdf'))

async def FindOldestUser(message):


    age = 0
    user = message.author

    async for member in message.guild.fetch_members(limit=None):
        print(member.name)
        if age <= member.created_at:
            age = member.created_at
            user = member

    message.channel.send("Eldest user is " + user.name)

@client.event
async def on_message(message):

    if(message.content == ""):
        return

    message_content = message.content

    if "<@799813917802364939>" in message_content:
        message_content = message_content.replace("<@799813917802364939>", "")
        message_content = message_content.strip()
    
    #print(message_content)

    if message.author == client.user:
        return

    if (message_content.startswith('$session')):
        await SetupSession(message)

    if(message_content.startswith('$x')):
        await Alert(message)

    if(message_content.startswith('$stopsession')):
        await StopSession(message)
    
    if(message_content.startswith('$checksessions')):
        await CheckSessions(message)

    if(message_content.startswith('$zabazoo')):
        await SendCharacters(message)

    if message_content.startswith('$quit') and message.author.id == 121406882865872901:
        global amOnline
        amOnline = False
        
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1) 

    #Secret Santa Commands
    if message_content.startswith("$enter"):
        await WriteAddress(message)

    if message_content.startswith("$remove"):
        await RemoveAddress(message)

    if message_content.startswith("$addycheck"):
        await CheckAddress(message)

    if message_content.startswith("$run") and message.author.id == 121406882865872901:
        await DistributeAddresses(message)

    if message_content.startswith("$local-run") and message.author.id == 121406882865872901:
        await LocalSecretSanta(message)

    if message_content.startswith('$help'):
        tmp = 
**Somewhere in each of these commands, you need to mention RoboGav in order for the command to work**
*If DM'ing the bot, this is not required. *

$enter - Used to enter your address in the format of <Street Address City, State Zipcode, Perferred Delivery Name>. Example: $enter 1111 Street Waco, Texas 78787, Gav

$check - see what address is used for your name. 

$remove - Used to remove your name and address from the pool. 

$check - Used to check current users signed up for Secret Santa. Example: $check

$wishlist - Used to add a single item to your wishlist. Example: $wishlist Cotton Candy

$mywishlist - Used to check your wishlist. Example: $mywishlist 

$fuck - You'll see

        await message.channel.send(tmp)

    if message_content.startswith('$check'):
        await checkUsers(message)

    if message_content.startswith('$wishlist'):
        await AddToWishList(message)

    if message_content.startswith('$mywishlist'):
        await CheckWishList(message)

    if message_content.startswith('$fuck'):
        await message.channel.send("Fuck off")

    if message_content.startswith ('$hohoho'):
        await message.channel.send("||ho ho ho||")

"""