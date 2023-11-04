import discord
from enum import Enum
import os
import random

class Genre(Enum):
    Battle = 0
    Tavern = 1
    Adventuring = 2
    Boss = 3

#region Audio Commands

def play_audio(voice_client:discord.VoiceClient, path_to_audio:str, after_behavior = None):
    if(voice_client.is_connected()):
        if(voice_client.is_playing() or voice_client.is_paused()): stop_audio(voice_client)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                                executable="C:/ffmpeg/bin/ffmpeg.exe", 
                                source=path_to_audio
                            ), 1.0)
        voice_client.play( source, 
                            after=lambda e: print(e) if e else after_behavior()
                        )
        return source
        
def stop_audio(voice_client:discord.VoiceClient):
    if(voice_client.is_connected()):
        if(voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()

def pause_audio(voice_client:discord.VoiceClient):
    if(voice_client.is_connected()):
        if(voice_client.is_playing()):
            voice_client.pause()

def resume_audio(voice_client:discord.VoiceClient):
    if(voice_client.is_connected()):
        if(voice_client.is_paused()):
            voice_client.resume()

def play_random_audio_from_directory(voice_client:discord.VoiceClient, path_to_audio_folder:str, after_behavior = None):
    if(voice_client.is_connected()):
        if(voice_client.is_playing()):
            return None
        elif (voice_client.is_paused()):
            voice_client.resume()
        else:
            sound = random.choice(os.listdir(path_to_audio_folder))
            file = os.path.join(path_to_audio_folder, sound)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                                    executable="C:/ffmpeg/bin/ffmpeg.exe", 
                                    source=file
                                ), 1.0)
            voice_client.play(source , 
                                after=lambda e: print(e) if e else after_behavior()
                            )
            return source
        
musicPath = os.getcwd() + "\Music"
def generate_song_queue(genre:Genre):
    audio_queue = []
    for single_file in os.listdir(musicPath + "\\" + genre.name):
        audio_queue.append(os.path.join(musicPath, genre.name, single_file))
    random.shuffle(audio_queue)
    return audio_queue

def pick_song_from_queue(audio_queue:list[str]):
    if(audio_queue.count() != 0):
        return audio_queue.pop()
    else:
        return None

        


#endregion     

#region Maths

def clamp(n, min, max):
    if n < min: return min
    elif n > max: return max
    else: return n


import re
def rolldice(dice_string:str):
    """
    This functions don't fucking work yet. 
    """
    
    pattern = re.compile(
        r"""
        (?P<dice_count>.\d+)
        d
        (?P<severity>.\d+)
        (?P<everything_else>.*)?
        """, re.IGNORECASE)

    match = re.search("""(?P<dice_count>.\d+)d(?P<severity>.\d+)(?P<everything_else>.*)?""", dice_string)
    num_dice = int(match.group("num_dice"))
    severity = int(match.group("severity"))
    everything_else = int(match.group("everything_else"))
    
    print(num_dice)
    print(severity)
    print(everything_else)

#endregion

#region File Handling
def register_channel(interaction: discord.Interaction):
    if(os.path.exists(os.path.join(os.getcwd(), f"Secret Santa/{interaction.channel_id}"))):
        return "Channel already registered."

    os.mkdir(os.path.join(os.getcwd(), f"Secret Santa/{interaction.channel_id}"))
    if(os.path.exists(os.path.join(os.getcwd(), f"Secret Santa/{interaction.channel_id}"))):
        return "Registered this channel for Secret Santa successfully!"
    else:
        return "Failed to register channel successfully, contact Gav."
        
def register_user(client:discord.Client, guild:discord.Guild, interaction:discord.Interaction, address:str):
    """
    Registers a user to a guild
    """
    channel_id = match_guild_to_channel(client, guild)
    if channel_id == None:
        return "Something went wrong. Contact Gav"

    channel_path = os.path.join(os.getcwd(), f"Secret Santa/{channel_id}")
    target_path = os.path.join(os.getcwd(), f"Secret Santa/{channel_id}/{interaction.user.id}")

    if(not os.path.exists(channel_path)):
        return "Channel appears to not be registered for secret santa."
    if(os.path.exists(target_path)):
        return "User already registered in this channel. To manage your wishlist or address, please open the Secret Santa UI again."
    z = open(f"{target_path}", "x")
    z.close()
    if(os.path.exists(target_path)):
        with open(target_path, 'w') as f:
            f.write(address)
        return "Registered user successfully. To manage your wishlist or address, please open the Secret Santa UI again."
    else:
        return "Failed to register user successfully."

def retrieve_channel_paths():
    channel_dirs = []
    for subdirs, dirs, files in os.walk(os.path.join(os.getcwd(), "Secret Santa")):
        channel_dirs.append(subdirs)
    return channel_dirs[1:]

def match_guild_to_channel(client:discord.Client, guild:discord.Guild):
    list_of_channel_ids = [os.path.basename(os.path.normpath(x)) for x in retrieve_channel_paths()]
    for channel_id in list_of_channel_ids:
        full_channel = client.get_channel(int(channel_id))
        maybe_guild = full_channel.guild.id
        if maybe_guild == guild.id:
            return channel_id
    return None



#endregion

#region User Management

async def fetch_guild(client:discord.Client, id:int):
    if client.is_ready():
        return client.get_guild(id)
    
async def fetch_channel(client:discord.Client, id:int):
    if client.is_ready():
        return client.get_channel(id)
    
async def fetch_channel_members(client:discord.Client, channel:discord.TextChannel):
    if client.is_ready():
        return channel.members

async def retrieve_users_registration(client:discord.Client, interaction: discord.Interaction):
    """
    Returns a list of Discord.Guilds that the user is registered in
    """
    channel_paths = retrieve_channel_paths()
    registered_channels = []
    for channel in channel_paths:
        for subdirs, dirs, users in os.walk(os.path.join(channel)):
            for user in users:
                if int(user) == interaction.user.id:
                    registered_channels.append(await fetch_channel(client, int(os.path.basename(os.path.normpath(channel)))))

    registered_guilds = [channel.guild for channel in registered_channels]
    return registered_guilds

async def retrieve_guilds_part_of(client:discord.Client, interaction:discord.Interaction):
    """
    Retruns a list of Discord.Guilds that a user is in but not necessarily registered for
    """
    channel_paths = retrieve_channel_paths()
    guilds = []
    for channel in channel_paths:
        discord_channel:discord.TextChannel = await fetch_channel(client, int(os.path.basename(os.path.normpath(channel))))
        for member in discord_channel.members:
            if(member.id == interaction.user.id):
                guilds.append(discord_channel.guild)
    return guilds
#endregion