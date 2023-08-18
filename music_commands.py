from typing import Any
import discord
from discord.interactions import Interaction
from bot import PlaySessionView, Genre
import utils


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