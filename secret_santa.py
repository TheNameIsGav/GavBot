import discord
from discord.ext import commands
from discord import app_commands
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

    async def fetch_guild(self, id:int):
        if self.client.is_ready():
            return self.client.get_guild(id)
        
    async def open_santa_ui(self, interaction: discord.Interaction):
        valid_guilds = await self.participating_events(interaction.user.id)
        secretSantaView = SecretSantaView(interaction, valid_guilds)
        await secretSantaView.startup()
        pass

    async def participating_events(self, id) -> [discord.Guild]:
        """
        Returns a list of guilds that a user is partaking in secret santa in
        """
        valid_guilds:[discord.Guild] = []

        p_guilds = self.get_participating_guilds()
        p_guilds = [await self.client.fetch_guild(x) for x in p_guilds]
        for guild in p_guilds:
            async for member in guild.fetch_members(): #This cannot be used on super large server
                if id == member.id:
                    valid_guilds.append(guild)
        return valid_guilds
    #endregion

    #region Sync Commands
    def register_guild(interaction: discord.Interaction):
        if(os.path.exists(os.path.join(os.getcwd(), f"Secret Santa/{interaction.guild_id}"))):
            return "Guild already registered. You can delete the registration if you would like."

        os.mkdir(os.path.join(os.getcwd(), f"Secret Santa/{interaction.guild_id}"))
        if(os.path.exists(os.path.join(os.getcwd(), f"Secret Santa/{interaction.guild_id}"))):
            return "Created Guild folder successfully."
        else:
            return "Failed to create Guild folder successfully. "

    """
    Returns a list of guilds that are participating in secret santa
    """
    def get_participating_guilds(self):
        participating_guilds = []

        root_dir = os.path.join(os.getcwd(), "Secret Santa")
        for subdir, dirs , files in os.walk(root_dir):
            for elem in dirs:
                participating_guilds.append(elem)

        return participating_guilds
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
        response = self.register_guild(interaction)
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
        self.add_option(label=0)
    
    def configure_options(self, guilds:[discord.Guild]):
        if len(guilds) == 0:
            self.disabled = True
            self.add_option(label="You probably shouldn't be seeing this. If you are, contact Gav.")
            return
        for guild in guilds:
            self.add_option(label=guild.name)


class SecretSantaView(discord.ui.View):
    interaction:discord.Interaction = None
    embed = None
    selectMenu = None

    def __init__(self, interaction:discord.Interaction, valid_guilds):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.selectMenu = GuildSelectMenu()
        self.selectMenu.configure_options(valid_guilds)
        self.add_item(self.selectMenu)

        self.embed = discord.Embed(title="Secret Santa", description="Stuff", color=0xffffff)

    async def startup(self):
        await self.interaction.response.send_message(embed=self.embed, view=self)
#endregion