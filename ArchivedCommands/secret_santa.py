from typing import Any, Coroutine
import discord
from discord.ext import commands
from discord import app_commands
from discord.interactions import Interaction
from utils import *
import datetime
import os
import logging

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
        self.rootpath = os.path.join(os.getcwd(), "Secret Santa")

    @app_commands.command(name="register", description="Registers a user to participate in this channels Secret Santa")
    async def register(self, interaction:discord.Interaction):
        print(f"{interaction.user.name} ran Register at {datetime.datetime.now()}")
        if(not is_registered_channel(self.rootpath, interaction.channel_id)):
            await interaction.response.send_message("I'm afraid the channel you ran this command in is not participating in Secret Santa. Please try this command in a registered channel. If you believe this message to be in error, please contact Gav.")
            return
        
        target_path = os.path.join(self.rootpath, f'{interaction.user.id}')
        if(not os.path.exists(target_path)):
           with open(f"{target_path}", "x") as f:
               f.write(f'{interaction.user.global_name}\n')
               f.write(f'{interaction.channel_id}')    
               await interaction.response.send_message("Registered successfully! Please use the /address command to update your address, and the /secret-santa help command to view additional functions!")
        else:
            channels = users_participating_channels(self.rootpath, interaction.user.id)
            if interaction.channel_id in channels:
                await interaction.response.send_message("You appear to already be registered to participate in Secret Santa here! Please use the /secret-santa help command to view additional functions!")
                return
            else:
                lines = []
                with open(target_path, "r") as f:
                    lines = f.readlines()
                    lines[1] = lines[1].strip() + f",{interaction.channel_id}"
                with open(target_path, "w") as f:
                    f.writelines(lines)
                await interaction.response.send_message("Registered successfully! Please use the /address command to update your address, and the /secret-santa help command to view additional functions!")
                return

    @app_commands.command(name="register_guild_channel", description="Registers a channel to participate in Secret Santa")
    async def register_guild_channel(self, interaction:discord.Interaction):
        lines = []
        print(f"{interaction.user.name} ran Register Guild at {datetime.datetime.now()}")
        if(not interaction.user.guild_permissions.administrator and not self.client.is_owner == interaction.user):
            await interaction.response.send_message("I'm afraid you are not an administrator. Please contact an admin to register this guild for Secret Santa")
            return

        if(is_registered_channel(self.rootpath, interaction.channel_id)):
            await interaction.response.send_message("Channel already registered!")
            return

        with open(f"{os.path.join(self.rootpath, 'Valid Guilds')}", "a") as f:
            f.write(f"{interaction.channel_id}\n")
            await interaction.response.send_message("Registered this channel for Secret Santa successfully!")
            return
        
    @app_commands.command(name="address", description="sets the address of the user")
    async def address(self,interaction:discord.Interaction):
        print(f"{interaction.user.name} ran Address at {datetime.datetime.now()}") 
        if(is_registered_user(self.rootpath, interaction.user.id)):
            self.address_feedback = AddressInput()
            self.address_feedback.on_submit = self.address_callback
            await interaction.response.send_modal(self.address_feedback)
        else:
            await interaction.response.send_message("You are not registered for any Secret Santa")

    async def address_callback(self, interaction:discord.Interaction):
        address = self.address_feedback.address.value

        lines = []
        with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "r") as f:
            lines = f.readlines()

        if len(lines) < 3:
            with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "w") as f:
                f.writelines(lines)
                f.write("\n" + address + "\n")
        else:
            lines[2] = address + "\n"
            with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "w") as f:
                f.writelines(lines)

        await interaction.response.send_message(f"Registered address as {address}", ephemeral=True)

    @app_commands.command(name="wishlist", description="Adds an item to the users wishlist")
    async def wishlist(self, interaction:discord.Interaction):
        print(f"{interaction.user.name} ran Wishlist at {datetime.datetime.now()}")
        if(is_registered_user(self.rootpath, interaction.user.id)):
            self.wishlist_feedback = WishlistInput()
            self.wishlist_feedback.on_submit = self.wishlist_callback
            await interaction.response.send_modal(self.wishlist_feedback)
        else:
            await interaction.response.send_message("You are not registered for any Secret Santa")

    async def wishlist_callback(self, interaction:discord.Interaction):
        item = self.wishlist_feedback.item.value
        lines = []
        with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "r") as f:
            lines = f.readlines()

        if len(lines) == 3:
            with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "w") as f:
                lines.append(item + "\n")
                f.writelines(lines)
        else:
            with open(f"{os.path.join(self.rootpath, f'{interaction.user.id}')}", "a") as f:
                f.write(item + "\n")

        await interaction.response.send_message(f"Added {item} to wishlist!", ephemeral=True)
    
    @app_commands.command(name="view_wishlist", description="View your current wishlist")
    async def view_wishlist(self, interaction:discord.Interaction):
        print(f"{interaction.user.name} ran View Wishlist at {datetime.datetime.now()}")
        if(not is_registered_user(self.rootpath, interaction.user.id)):
            await interaction.response.send_message("You are not registered for any Secret Santa")
            return
        
        items = get_users_wishlist(self.rootpath, interaction.user.id)
        self.embed = discord.Embed()
        self.embed.title = "Wishlist Items"
        for i in range(0, len(items)):
            self.embed.add_field(name=f"Item {i+1}", value=items[i], inline=False)

        await interaction.response.send_message(embed=self.embed, ephemeral=True)

    @app_commands.command(name="remove_item", description="removes an item from your wishlist")
    async def remove_item(self, interaction:discord.Interaction, index:int):
        """Removes an item from your wishlist - irreversable

        Parameters
        -----------
        Item _: int
            The item number to remove
        """
        print(f"{interaction.user.name} ran Remove Item at {datetime.datetime.now()}")
        if(not is_registered_user(self.rootpath, interaction.user.id)):
            await interaction.response.send_message("You are not registered for any Secret Santa")
            return
        
        await interaction.response.send_message(remove_item_from_wishlist(self.rootpath, interaction.user.id, index), ephemeral=True)
    
    @app_commands.command(name="help", description="Lists out the commands for Secret Santa")
    async def help(self, interaction:discord.Interaction):
        #remove_item
        #view_wishlist
        #wishlist
        #address
        #register

        print(f"{interaction.user.name} ran Help at {datetime.datetime.now()}")

        self.embed = discord.Embed()
        self.embed.add_field(inline=False, name="/secret-santa remove_item <index>", value="Removes the item in your wishlist at index")
        self.embed.add_field(inline=False, name="/secret-santa view_wishlist", value="View your wishlist. No one else can see this.")
        self.embed.add_field(inline=False, name="/secret-santa wishlist", value="Opens a dialogue box for you to enter an item to put on your wishlist. No one else can see this.")
        self.embed.add_field(inline=False, name="/secret-santa address", value="Opens a dialgoue box for you to enter your address. Use again to modify. No one else can see this.")
        self.embed.add_field(inline=False, name="/secret-santa register", value="Registers you to participate in Secret Santa. Only usable in the channel where Secret Santa began.")
        self.embed.add_field(inline=False, name="/secret-santa view_address", value="View your current address as set in Secret Santa.")
        await interaction.response.send_message(embed=self.embed)
    
    @app_commands.command(name="view_address", description="Views address")
    async def view_address(self, interaction:discord.Interaction):
        print(f"{interaction.user.name} ran View Address at {datetime.datetime.now()}")
        if(not is_registered_user(self.rootpath, interaction.user.id)):
            await interaction.response.send_message("You are not registered for any Secret Santa")
            return
        
        addy = get_users_address(self.rootpath, interaction.user.id)
        await interaction.response.send_message(f"Your address is currently set as\n **{addy}**", ephemeral=True)


    @app_commands.command(name="distribute", description="Distributes the wishlists for Secret Santa in this channel!")
    async def distribute(self, interaction:discord.Interaction):
        debug = False
        #if(not interaction.user.guild_permissions.administrator):
            #await interaction.response.send_message("I'm afraid you cannot run that command as you are not an admin.")
            #return
        
        await interaction.response.send_message(content=("Application is in DEBUG MODE. Testing..." if debug else "Sending..."))

        participating_users = get_participating_users(self.rootpath, interaction.channel_id)
        matchups = matchup(participating_users)
        if(matchups == None):
            await interaction.response.send_message("Yeah something went wrong get fucked, try again")
            return
        
        actual_users = {user: self.client.get_user(user) for user in participating_users}

        for (user, target) in matchups:
            dm_embed = discord.Embed()
            dm_embed.title = "TEST SECRET SANTA NOT REAL" if debug else "Secret Santa!"
            dm_embed.add_field(inline=False, name="Target", value=f"{actual_users[target].display_name}")
            dm_embed.add_field(inline=False, 
                               name="Address", 
                               value="Application in Debug Mode" if debug else f"{get_users_address(self.rootpath, target)}")
            
            wishlist = get_users_wishlist(self.rootpath, target)
            wishlist_string = ""
            i = 0
            for item in wishlist:
                i+=1
                wishlist_string += f"{i}: {item.strip()}\n"
            dm_embed.add_field(inline=False, name="Wishlist", value=wishlist_string)

            user_discord_actual = self.client.get_user(121406882865872901) if debug else self.client.get_user(user)
            if(user_discord_actual.dm_channel != None):
                await user_discord_actual.send(embed=dm_embed)
            else:
                await self.client.create_dm(user_discord_actual)
                await user_discord_actual.send(embed=dm_embed)

        await interaction.followup.send(content = ("Application is in DEBUG MODE. Tested" if debug else "Sent!"))

class AddressInput(discord.ui.Modal, title="Address"):
    address = discord.ui.TextInput(
        label="Address",
        placeholder="Taylor Swift, 1111 Thing St. Austin TX. 78707"
    )

class WishlistInput(discord.ui.Modal, title="Item you'd like"):
    item=discord.ui.TextInput(
        label="Item",
        placeholder="Consider putting your Amazon Wishlist as one of your items!"
    )