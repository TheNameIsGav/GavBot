import discord
from discord import app_commands
from discord.ext import commands
import re

from utils import Log

PREPOSITIONS = [
    "a", "an", "as", "at", "and", "but", "be", "by", "for", "from", "in", "is", "it", "like", "of", "to", "the", "that", "this", "than", "then", "i", "me", "you", ""
]

class UserStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_message_stats_user(
        self,
        user: discord.User,
        guild: discord.Guild,
        channel: discord.TextChannel = None
    ):
        """Fetches message stats for a specific user optionally in a specific channel."""
        message_stats = {
            "messages": 0,
            "words": 0,
            "embeds": 0,
            "last_update": None,
            "unique_channels": set(),
            "most_used_word": "",
            "most_responded_user": "",
            "longest_message": 0
        }

        if channel is None:
            channels = guild.text_channels
        else:
            channels = [channel]

        replied_users = {}
        most_used_word = {}

        for channel in channels:
            Log(f"Fetching messages from channel: {channel.name}", loggerName="stats")
            count = 0
            try:
                async for message in channel.history(limit=15000):
                    count+=1
                    if(count % 100 == 0):
                        Log(f"Message count: {count} for channel {channel.name}", loggerName="stats")

                    if message.author != user:
                        continue

                    # Last Sent Message
                    if (
                        message_stats["last_update"] is None
                        or message.created_at > message_stats["last_update"]
                    ):
                        message_stats["last_update"] = message.created_at

                    #Message Count
                    message_stats["messages"] += 1

                    #Word Count
                    message_stats["words"] += len(message.content.split())

                    #Embeds
                    if message.embeds or message.attachments:
                        message_stats["embeds"] += 1

                    #Unique Channels
                    message_stats["unique_channels"].add(channel.id)

                    # Longest Message
                    if(message_stats["words"] > message_stats["longest_message"]):
                        message_stats["longest_message"] = message_stats["words"]

                    #Get the person that our user replied to the most
                    try: 
                        if message.reference is not None and message.reference.message_id is not None:
                            msg:discord.PartialMessage = channel.get_partial_message(message.reference.message_id)
                            reply_id = (await msg.fetch()).author.id
                            if(reply_id in replied_users.keys()):
                                replied_users[reply_id] += 1
                            else:
                                replied_users[reply_id] = 1
                    except discord.NotFound:
                        print("message not found")

                    #Get most used word
                    for word in message.content.split():
                        mod_word = word.strip().lower()
                        mod_word = re.sub(r'[^a-zA-Z]', '', mod_word)
                        if(mod_word not in PREPOSITIONS):
                            if(mod_word in most_used_word.keys()):
                                most_used_word[mod_word] += 1
                            else:
                                most_used_word[mod_word] = 1
            except:
                continue

        #Get the person that our user replied to the most 
        most_replied_user_IDs = [(k, v) for k, v in sorted(replied_users.items(), key=lambda item: item[1])]
        print(most_replied_user_IDs)
        if(len(most_replied_user_IDs) > 0):
            most_replied_user_ID = most_replied_user_IDs.pop()[0]
            member = guild.get_member(most_replied_user_ID)  # Try to get the member from cache
            if member is None:
                try:
                    display_name = (await guild.fetch_member(most_replied_user_ID)).display_name  # Fetch if not in cache
                except discord.NotFound:
                    display_name = "User doesn't exist, this is a bug"
            else:
                display_name = member.display_name
            message_stats["most_responded_user"] = display_name
        else: 
            message_stats["most_responded_user"] = "User has never replied to another user."

        #Most used word
        most_used_words = [(k, v) for k, v in sorted(most_used_word.items(), key=lambda item: item[1])]
        Log(f"Most used word list {most_used_words}", loggerName="stats")
        most_used_word = most_used_words.pop()
        Log(f"Most used word {most_used_word}", loggerName="stats")
        message_stats["most_used_word"] = most_used_word

        return message_stats

    @app_commands.command(
        name="wordstats", description="Fetches stats for a user in a channel for the last 15000 message. This takes ~5 mins - be patient."
    )
    async def wordstats(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        channel: discord.TextChannel = None,
    ):
        await interaction.response.defer()

        if channel is None:
            search_name = interaction.guild.name
            message_stats = await self.fetch_message_stats_user(
                user, guild=interaction.guild
            )
        else:
            search_name = channel.name
            message_stats = await self.fetch_message_stats_user(
                user, guild=interaction.guild, channel=channel
            )

        messages_sent = message_stats["messages"]
        words_sent = message_stats["words"]
        words_per_message = (
            message_stats["words"] / message_stats["messages"]
            if message_stats["messages"] > 0
            else 0
        )

        stat_message = (
            f"**Stats for {user.display_name} in {search_name}:**\n"
            f"Messages Sent: {messages_sent}\n"
            f"Words Sent: {words_sent}\n"
            f"Words per Message: {words_per_message:.2f}\n"
            f"Embeds/Attachments: {message_stats['embeds']}\n"
            f"Across {len(message_stats['unique_channels'])} unique channels\n"
            f"Most used word is '{message_stats['most_used_word'][0]}' with {message_stats['most_used_word'][1]} uses.\n"
            f"Most replied to user: {message_stats['most_responded_user']}\n"
        )

        await interaction.followup.send(stat_message)
