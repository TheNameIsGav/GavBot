from utils import *
from discord.ext import commands
from discord import app_commands
from discord.interactions import Interaction
import logging

import os

class TaskSession(commands.GroupCog, group_name="task"):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.rootpath = os.path.join(os.getcwd(), "Task")

    @app_commands.command(name="viewtasks", description="View's current tasks and rewards")
    async def viewtasks(self, interaction:discord.Interaction):
        
        self.save_tasks(interaction.user.id)
        
    def save_tasks(self, user_id):
        return
    