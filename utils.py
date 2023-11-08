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


def is_registered_channel(rootpath, channel_id):
    with open(f"{os.path.join(rootpath, 'Valid Guilds')}", "r") as f:
        lines = f.readlines()

        for line in lines:
            if int(line.strip()) == channel_id:
                return True
        return False
    
def users_participating_channels(rootpath, user_id):
    with open(f"{os.path.join(rootpath, f'{user_id}')}", "r") as f:
        lines = f.readlines()
        lines = lines[1:]
        channel_ids = [int(channel_id) for channel_id in lines[0].split(',')]
        return channel_ids
    
def is_registered_user(rootpath, user_id):
    for subdirs, dirs, files in os.walk(rootpath):
        for file in files:
            if(int(file) == user_id):
                return True
    return False

def get_users_wishlist(rootpath, user_id):
    lines = []
    with open(f"{os.path.join(rootpath, f'{user_id}')}", "r") as f:
        lines = f.readlines()
    return lines[3:]
        
def remove_item_from_wishlist(rootpath, user_id, index):
    index = index - 1
    lines = []
    with open(f"{os.path.join(rootpath, f'{user_id}')}", "r") as f:
        lines = f.readlines()

    wishlist_items = lines[3:]
    pre_content = lines[:3]
    if index in range(0, len(wishlist_items)):
        item = wishlist_items[index]
        del wishlist_items[index]
        with open(f"{os.path.join(rootpath, f'{user_id}')}", "w") as f:
            f.writelines(pre_content)
            f.writelines(wishlist_items)
        return f"Removed item {item}"
    else:
        return "Invalid item number to remove."