from typing import Any
import discord
from discord.interactions import Interaction
import utils

activeSessions = {}

# class PlaySessionView(discord.ui.View):
#     genre:Genre = Genre.Adventuring
#     voice_channel = None
#     voice_client:discord.VoiceClient = None
#     interaction:Interaction = None
#     embed = None
#     source:discord.PCMVolumeTransformer = None
#     song_queue = []
    
#     #region Buttons
#     battleButton = None
#     adventuringButton = None
#     tavernButton = None
#     bossButton = None    
#     playPauseButton = None
#     loopButton = None
#     volumeUpButton = None
#     volumeDownButton = None
#     skipFowardButton = None
#     skipBackwardsButton = None
#     #endregion

#     async def update_ui(self):
#         await self.interaction.response.edit_message(embed=self.embed, view=self)

#     def pick_new_song(self):
#         stop_audio(self.voice_client)
#         sound = random.choice(os.listdir(musicPath + "\\" + self.genre.name))
#         file = os.path.join(musicPath, self.genre.name, sound)
#         self.source = play_audio(self.voice_client, file, self.pick_new_song())
#         if(self.source == None): 
#             print("Something went wrong.")
#             return
        
#         self.song_queue.append(file)


#     def __init__(self, interaction:discord.Interaction):
#         super().__init__(timeout=None)
#         self.interaction = interaction

#         self.battleButton = mc.BattleButton(self)
#         self.add_item(self.battleButton)

#         self.adventuringButton = mc.AdventuringButton(self)
#         self.add_item(self.adventuringButton)

#         self.tavernButton = mc.TavernButton(self)
#         self.add_item(self.tavernButton)

#         self.bossButton = mc.BossButton(self)
#         self.add_item(self.bossButton)

#         self.volumeUpButton = mc.VolumeUpButton(self)
#         self.add_item(self.volumeUpButton)

#         self.playPauseButton = mc.PlayPauseButton(self)
#         self.add_item(self.playPauseButton)

#         self.volumeDownButton = mc.VolumeDownButton(self)
#         self.add_item(self.volumeDownButton)

#         self.skipBackwardsButton = mc.SkipBackwardsButton(self)
#         self.add_item(self.skipBackwardsButton)

#         self.loopButton = mc.LoopButton(self)
#         self.add_item(self.loopButton)

#         self.skipFowardButton = mc.SkipFowardButton(self)
#         self.add_item(self.skipFowardButton)

#     async def startup(self):
#         print(f"Starting new play session for guild: {self.interaction.guild.name}")
#         voice_channel = self.interaction.user.voice.channel
#         if(voice_channel == None): 
#             await self.interaction.response.send_message("User is not connected to a voice channel")
#             return
        
#         activeSessions[self.interaction.guild_id] = self
#         self.voice_client = await voice_channel.connect()

#         self.embed = discord.Embed(title = "Not playing", description="not playing", color=0xffffff)
#         await self.interaction.response.send_message(embed=self.embed, view=self)

#     def changeGenre(self, value:Genre):
#         self.genre = value

#         self.battleButton.disabled = False
#         self.battleButton.style = discord.ButtonStyle.gray

#         self.adventuringButton.disabled = False
#         self.adventuringButton.style = discord.ButtonStyle.gray

#         self.bossButton.disabled = False
#         self.bossButton.style = discord.ButtonStyle.gray

#         self.tavernButton.disabled = False
#         self.tavernButton.style = discord.ButtonStyle.gray
#         match(value):
#             case Genre.Battle:
#                 self.battleButton.disabled = True
#                 self.battleButton.style = discord.ButtonStyle.green
#                 pass
#             case Genre.Adventuring:
#                 self.adventuringButton.disabled = True
#                 self.adventuringButton.style = discord.ButtonStyle.green
#                 pass
#             case Genre.Tavern:
#                 self.tavernButton.disabled = True
#                 self.tavernButton.style = discord.ButtonStyle.green
#                 pass
#             case Genre.Boss:
#                 self.bossButton.disabled = True
#                 self.bossButton.style = discord.ButtonStyle.green
#                 pass
#         self.playSong()
#         pass


class PlayPauseButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.success, label="⏸", row=1)
        self.parent = parent

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        if(self.parent.voice_client.is_playing()):
            utils.pause_audio(self.parent.voice_client)
            self.style = discord.ButtonStyle.red
            self.label = "⏵"
        elif(self.parent.voice_client.is_paused()):
            utils.resume_audio(self.parent.voice_client)
            self.style = discord.ButtonStyle.success
            self.label = "⏸"
        await self.parent.update_ui()


class SkipFowardButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="⏭", row=2)
        self.parent = parent

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        self.parent.pick_new_song()
        await self.parent.update_ui()
  

class SkipBackwardsButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="⏮", row=2)
        self.parent = parent

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()
        if(self.parent.song_queue.count == 1): 
            utils.play_audio(self.parent.voice_client, 
                             self.parent.song_queue[0],
                             self.parent.pick_new_song()
                             )
        else:
            utils.play_audio(self.parent.voice_client,
                             self.parent.song_queue[-2])
        await self.parent.update_ui()


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

    async def callback(self, interaction: Interaction):
        self.parent.source.volume = utils.clamp(self.parent.source.volume + .1, 0, 1)
        await interaction.response.defer()
        await self.parent.update_ui()


class VolumeDownButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="↓", row=1)
        self.parent = parent

    async def callback(self, interaction: Interaction):
        self.parent.source.volume = utils.clamp(self.parent.source.volume - .1, 0, 1)
        await interaction.response.defer()
        await self.parent.update_ui()
        

class BattleButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Battle", row=0)
        self.parent = parent

    async def callback(self, interaction):
        await interaction.response.defer()
        self.parent.changeGenre(Genre.Battle)


class TavernButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Tavern", row=0)
        self.parent = parent

    async def callback(self, interaction):
        await interaction.response.defer()
        self.parent.changeGenre(Genre.Tavern)


class AdventuringButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Adventuring", row=0)
        self.parent = parent

    async def callback(self, interaction):
        await interaction.response.defer()
        self.parent.changeGenre(Genre.Adventuring)


class BossButton(discord.ui.Button):
    parent:PlaySessionView = None

    def __init__(self, parent:PlaySessionView):
        super().__init__(style=discord.ButtonStyle.gray, label="Boss", row=0)
        self.parent = parent

    async def callback(self, interaction):
        await interaction.response.defer()
        self.parent.changeGenre(Genre.Boss)