from utils import *
from discord.ext import commands
from discord import app_commands
from discord.interactions import Interaction
import datetime
import json
import asyncio

import os

class TaskSession(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.rootpath = os.path.join(os.getcwd(), "Task/tasks.tasks")

        #Upon init calculate seconds until next hour to align timers
        now = datetime.datetime.now(datetime.timezone.utc)
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        time_remaining = next_hour - now
        seconds_remaining = time_remaining.total_seconds()

        #If we have less than 30 minutes until the next hour, fallover to the next hour. 
        if(seconds_remaining <= 30*60):
            seconds_remaining += 3600

        #self.t = threading.Timer(5, self.remind_tasks())
        self.task = asyncio.create_task(self.repeat_function(10))
        #print(f"Started reminder timer at {datetime.datetime.now(datetime.timezone.utc)}, scheduled for remind at {datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds_remaining)}")
        #self.t.start()

    async def repeat_function(self, interval):
        while True:
            await asyncio.sleep(interval)
            if(self.client.is_ready()):
                print("Client ready and executing reminder")
                await self.remind_tasks()
            else:
                print(f"client not ready, waiting {interval} seconds")
            
    async def remind_tasks(self):
        #remove remind frequency unless user reminds again so that in the case of a restart we can go and restart our timers
        with open(self.rootpath, "r") as f:
            for line in f.readlines():
                y = json.loads(line)
                if y["reminder_point"] is not None :
                    #if(datetime.datetime.strptime(y["reminder_point"]) < datetime.datetime.now(datetime.timezone.utc)):
                    await self.remind_task(y)
    
    async def remind_task(self, task):
        user = await self.client.fetch_user(task["id"])
        if user is not None:
            dm_channel = user.dm_channel
            if dm_channel is None:
                dm_channel = await user.create_dm()
            await dm_channel.send("blah blah test message on remind")
    
    def create_task(self, user_id, title, priority:int = 0, description=None, reminder:int = None):
        """
        Takes in a user_id, a title, an optional description, an optional priority, and an optional reminder duration in hours to remind the user of their task through Discord. 
        """
        task = {
            "task_id": hash(datetime.datetime.now(datetime.timezone.utc)), 
            "id": user_id,
            "title": title,
            "description": description,
            "priority": priority,
            "reminder_point": None
        }

        if reminder is not None:
            task["reminder_point"] = hour_rounder(datetime.datetime.now(datetime.timezone.utc)) + datetime.timedelta(hours=reminder)

        with open(self.rootpath, "a") as f:
            f.write(f"{json.dumps(task, default=str)}\n")
            Log("Created and dumped task", loggerName="tasks")

    def get_tasks(self, user_id):
        return