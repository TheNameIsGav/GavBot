import discord
from discord.ext import commands
from discord import app_commands
import os
import xml.etree.ElementTree as ET
import json
import random
from collections import defaultdict

class ChoreDistributor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_dir = os.path.join(os.getcwd(), "Chores", "Daily", "daily.xml")
        self.weekly_dir = os.path.join(os.getcwd(), "Chores", "Weekly", "weekly.xml")
        self.user_file = "Chores/target_user_ids.txt"
        self.assignment_file = "Chores/last_assignments.json"

    def load_user_ids(self):
        try:
            with open(self.user_file, "r") as f:
                return [int(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def load_chores(self, file_path):
        """Load all chores from a single XML file."""
        chores = []
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            return chores

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for elem in root.findall("chore"):
                chore = {
                    "name": elem.findtext("name", default="Unnamed chore"),
                    "description": elem.findtext("description", default=""),
                    "room": elem.findtext("room", default=""),
                    "frequency": elem.findtext("frequency", default=""),
                    "standard": elem.findtext("cleanliness_standard", default=""),
                }
                chores.append(chore)
        except ET.ParseError as e:
            print(f"❌ Failed to parse chore file {file_path}: {e}")
        return chores
    
    def distribute_evenly(self, chores, user_ids):
        assignments = defaultdict(list)
        if not user_ids:
            return assignments

        random.shuffle(chores)
        for i, chore in enumerate(chores):
            user_id = user_ids[i % len(user_ids)]
            assignments[user_id].append(chore)
        return assignments

    def save_assignments(self, daily, weekly):
        data = {
            "daily": {str(uid): chores for uid, chores in daily.items()},
            "weekly": {str(uid): chores for uid, chores in weekly.items()},
        }
        with open(self.assignment_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_assignments(self):
        if not os.path.exists(self.assignment_file):
            return {}, {}
        with open(self.assignment_file, "r") as f:
            data = json.load(f)
        return (
            {int(uid): chores for uid, chores in data.get("daily", {}).items()},
            {int(uid): chores for uid, chores in data.get("weekly", {}).items()},
        )

    def format_assignments_embed(self, daily_assignments, weekly_assignments, user_ids):
        embed = discord.Embed(title="Current Chore Assignments", color=discord.Color.green())
        for user_id in user_ids:
            user = self.bot.get_user(user_id)
            if not user:
                continue
            chore_list = ""
            for chore in daily_assignments.get(user_id, []):
                chore_list += f"🟢 **[Daily] {chore['name']}** - {chore['room']}\n"
            for chore in weekly_assignments.get(user_id, []):
                chore_list += f"🔵 **[Weekly] {chore['name']}** - {chore['room']}\n"
            if chore_list:
                embed.add_field(name=f"{user.display_name}", value=chore_list, inline=False)
        return embed

    async def distribute_chores(self):
        """Automatically runs weekly: assigns chores, saves, and sends them to each user via DM."""
        user_ids = self.load_user_ids()
        daily_chores = self.load_chores(self.daily_dir)
        weekly_chores = self.load_chores(self.weekly_dir)

        daily_assignments = self.distribute_evenly(daily_chores, user_ids)
        weekly_assignments = self.distribute_evenly(weekly_chores, user_ids)

        self.save_assignments(daily_assignments, weekly_assignments)

        # DM each user their assignments
        for user_id in user_ids:
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            if not user:
                continue

            daily = daily_assignments.get(user_id, [])
            weekly = weekly_assignments.get(user_id, [])

            if not daily and not weekly:
                continue

            msg = "**🧹 Your Chore Assignments This Week:**\n\n"
            for chore in daily:
                msg += f"🟢 **[Daily] {chore['name']}** ({chore['room']})\n"
            for chore in weekly:
                msg += f"🔵 **[Weekly] {chore['name']}** ({chore['room']})\n"
            try:
                await user.send(msg)
            except discord.Forbidden:
                print(f"⚠️ Couldn't DM {user_id} - DMs might be disabled.")

        print("✅ Weekly chores distributed and messages sent.")

    @app_commands.command()
    @commands.is_owner()
    async def admin_chore_tester(self, interaction: discord.Interaction):
        await interaction.response.pong()
        await self.distribute_chores()

    @app_commands.command(name="current_chores", description="View your current chore assignments.")
    async def current_chores(self, interaction: discord.Interaction):
        """Displays current chore assignments to the user, if they're on the list."""
        user_ids = self.load_user_ids()

        if interaction.user.id not in user_ids:
            await interaction.response.send_message(
                "🚫 You are not on the chore list and cannot view assignments.",
                ephemeral=True
            )
            return

        daily_assignments, weekly_assignments = self.load_assignments()
        user_id = interaction.user.id
        daily = daily_assignments.get(user_id, [])
        weekly = weekly_assignments.get(user_id, [])

        if not daily and not weekly:
            await interaction.response.send_message(
                "⚠️ You have no chores assigned yet. You actually should not ever see this message. If you do please message Gav"
            )
            return

        msg = "**🧹 Your Chore Assignments:**\n\n"
        for chore in daily:
            msg += f"🟢 **[Daily] {chore['name']}** ({chore['room']})\n"
        for chore in weekly:
            msg += f"🔵 **[Weekly] {chore['name']}** ({chore['room']})\n"

        await interaction.response.send_message(msg)