import discord
from enum import Enum
import os
import random
import datetime

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

#region Maths and Time

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

def hour_rounder(t:datetime.datetime):
    """
    Rounds a given DateTime T to the nearest hour at a 30 min breakpoint
    """
    return (t.replace(second=0, microsecond=0, hour=t.hour)+datetime.timedelta(hours=t.minute//30))

#endregion

#region Secret Santa
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

def get_users_address(rootpath, user_id):
    lines = []
    with open(f"{os.path.join(rootpath, f'{user_id}')}", "r") as f:
        lines = f.readlines()
    return lines[2]
        
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
    
def get_participating_users(rootpath, channel_id:int):
    """
    Gets a list of user id's as int's who are participating in a channel
    """
    user_ids = []

    for subdirs, dirs, files in os.walk(rootpath):
        for file in files:
            if file != 'Valid Guilds' and file != "MATCHUPS":
                with open(os.path.join(rootpath, file), "r") as f:
                    lines = f.readlines()
                    guilds = lines[1]
                    guilds = [int(x) for x in guilds.split(",")]
                    if channel_id in guilds:
                        user_ids.append(int(file)) #Change this to int(file)

    return user_ids     

exclusions:list[()] = [
    (121406882865872901, 306948002483011584), 
    (121406882865872901, 106048316420141056), 
    (106048316420141056, 121406882865872901), 
    (189567695371370496, 223619701027110913), 
    (106048316420141056, 227610442309042176), 
    (210977628545351680, 189567695371370496), 
    (214079671652843521, 121406882865872901), 
    (306948002483011584, 106048316420141056), 
    (223619701027110913, 214079671652843521), 
]

def matchup(user_ids:list[int]):
    """
    Given a list of users generates a Secret Santa List
    """
    success = False
    outcome:list[()] = []
    attempts = 0

    while(not success and attempts < 100):
        the_hat:list[int] = user_ids.copy()
        outcome:list[()] = []
        for user in user_ids:
            target = random.choice(the_hat)
            the_hat.remove(target)
            outcome.append((user, target))

        success = True
        for items in outcome:
            if items[0] == items[1] or items in exclusions:
                success = False
     
        attempts += 1
        if(attempts == 100): 
            return None
    
    text = ""
    for item in outcome:
        text += f"{item[0]} got {item[1]}\n"
        with open(os.path.join(os.getcwd(), "Secret Santa", "MATCHUPS"), "w") as f:
            f.writelines(text)
    
    return outcome
#endregion

#region Logging

import logging

class LogStatus(Enum):
    INF = 1
    ERR = 2 

def Log(incomingStr, logStatus: LogStatus = LogStatus.INF, loggerName:str = None):
    log = logging.getLogger(loggerName)
    #update_log_hander(logging.getLogger())
    transformed_string = f"{incomingStr}"
    if(logStatus == LogStatus.INF):
        #print(f"[INFO: {loggerName}] {transformed_string}")
        log.info(transformed_string)
    elif(logStatus == LogStatus.ERR):
        #print(f"[ERROR: {loggerName}] {transformed_string}")
        log.error(transformed_string)
    else:
        print(f"Something weird happened, logging to console:{datetime.datetime.now()} {transformed_string}")

def update_log_hander(logger):
    log_dir = f"{os.getenv('CUSTOMPATH')}"
    os.makedirs(log_dir, exist_ok=True)
    today_str = datetime.datetime.today().strftime(f"%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"{today_str}.log")

    current_handlers = logger.handlers[:]
    for handler in current_handlers:
        if isinstance(handler, logging.FileHandler):
            if(handler.baseFilename != log_filename):
                logger.removeHandler(handler)
                handler.close()

                new_handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")
                new_handler.setFormatter("[%(asctime)s] %(levelname)s: %(message)s")
                logger.addHandler(new_handler)
                logger.info("Log file updated to today's date")


#endregion