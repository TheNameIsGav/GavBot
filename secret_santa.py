from typing import Any, Coroutine
import discord
from discord.ext import commands
from discord import app_commands
from discord.interactions import Interaction
from utils import *
import os

#You should be able to see the current participants
#You should be able to add your address
#You should be able to edit your address
#You should be able to add an item to your wishlist
#you should be able to remove an item from your wishlist
#You should be able to see who you are getting a gift for once they have been assigned
#They should be seperated by guild
#Users should be able to select which guild they want to be a part of secret santa for

#DM the bot with a homepage - at first it just shows you a "join" button that you can select from appropriate guilds
#An admin with bot permissions should be able to add the server to participating guilds. 

#Guild Folder - Folder
    # User ID - Folder
        #Address - File
        #Wishlist - File  

class SecretSanta(commands.GroupCog, group_name="secret-santa"):

    def __init__(self, client: commands.Bot):
        self.client = client
        self._last_member = None

    #region Async Commands            
    async def open_santa_ui(self, interaction: discord.Interaction):
        guilds = await retrieve_guilds_part_of(self.client, interaction)
        secretSantaView = SecretSantaView(self.client, interaction)
        await secretSantaView.startup(guilds)
        pass
    #endregion

    #region Discord Commands
    @app_commands.command(name="cogtest")
    async def ping(self, interaction:discord.Interaction):
        bot_latency = round(self.client.latency * 1000)
        await interaction.response.send_message(f"Pong! {bot_latency} ms.")

    @app_commands.command(name="register_secret_santa", description="Registers a guild to participate in Secret Santa if not already registered.")
    async def register_secret_santa(self, interaction: discord.Interaction):
        channelType = interaction.channel.type
        if(channelType == discord.ChannelType.private and interaction.permissions.administrator):
            await interaction.response.send_message("Please re-run command in a valid guild or as an administrator!")
            return
        response = register_channel(interaction)
        await interaction.response.send_message(response)

    @app_commands.command(name="open_secret_santa", description="Opens the secret Santa Homepage Panel")
    async def open_secret_santa(self, interaction: discord.Interaction):
        channelType = interaction.channel.type
        # if(channelType != discord.ChannelType.private):
        #     await interaction.response.send_message("Please re-run command in our dms!")
        #     return
        await self.open_santa_ui(interaction)

    #endregion

#region UI
class GuildSelectMenu(discord.ui.Select):
    def __init__(self):
        super().__init__()
    
    def configure_options(self, guilds:[discord.Guild]):
        if len(guilds) == 0:
            self.disabled = True
            self.add_option(label="You probably shouldn't be seeing this. If you are, contact Gav.")
            return
        for guild in guilds:
            self.add_option(label=guild.name, value=guild.id)


class SecretSantaView(discord.ui.View):
    interaction:discord.Interaction = None
    client:discord.Client = None
    embed = None
    selectMenu = None
    selectedGuild = None
    addy = None

    def __init__(self, client:discord.Client, interaction:discord.Interaction):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.client = client

        self.selectMenu = GuildSelectMenu()

        self.manageButton = ManageButton()
        self.manageButton.callback = self.manage_callback

        self.registerButton = RegisterButton()
        self.registerButton.callback = self.register_callback

        self.deregisterButton = DeregisterButton()
        self.deregisterButton.callback = self.deregister_callback

    async def startup(self, guilds:[discord.Guild]):

        if(guilds == []):
            await self.interaction.response.send_message("It would appear that you're not a part of any channel in any guild that is participating in Secret Santa. Please contact an admin if you think this is in error.")

        self.selectMenu.configure_options(guilds)
        self.selectMenu.callback = self.guild_selection_callback
        self.add_item(self.selectMenu)

        await self.interaction.response.send_message("Please select the Server you like to manage or register for.", view=self)

    async def guild_selection_callback(self, interaction:discord.Interaction):
        selectedGuild = self.selectMenu.values[0]
        print(f"Selected {selectedGuild}")

        selectedGuild = await fetch_guild(self.client, int(selectedGuild))
        self.selectedGuild = selectedGuild
        self.remove_item(self.selectMenu)
        if selectedGuild in await retrieve_users_registration(self.client, self.interaction):
            self.add_item(self.manageButton)
            self.add_item(self.deregisterButton)
        else:
            self.add_item(self.registerButton)
        self.selectMenu.disabled = True
        await interaction.response.send_message(f"Selected Guild {selectedGuild.name}", view=self)
        
    async def register_callback(self, interaction:discord.Interaction):
        self.addy = AddressInput()
        self.addy.on_submit = self.address_submit
        self.registerButton.disabled = True
        await interaction.response.send_modal(self.addy)
        
    async def manage_callback(self, interaction:discord.Interaction):
        self.manageButton.disabled = True
        await interaction.response.send_message("Pushed manage")
        
    async def deregister_callback(self, interaction:discord.Interaction):
        self.deregisterButton.disabled = True
        await interaction.response.send_message("Pushed deregister")

    async def address_submit(self, interaction:discord.Interaction):
        await interaction.response.send_message(register_user(self.client, self.selectedGuild, interaction, self.addy.address.value), ephemeral=True)
        

class RegisterButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.success, label="Register")

class ManageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style = discord.ButtonStyle.blurple, label="Manage")

class DeregisterButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style= discord.ButtonStyle.red, label="Deregister")

class AddressInput(discord.ui.Modal, title="Address"):
    address = discord.ui.TextInput(
        label="Address",
        placeholder="1111 Thing St. Taylor Swift, Austin TX. 78707"
    )
#endregion