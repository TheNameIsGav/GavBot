from openai import OpenAI, RateLimitError, BadRequestError, AuthenticationError, APIConnectionError, OpenAIError
from dotenv import load_dotenv
import os
import asyncio
import traceback
import random

# define a retry decorator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

load_dotenv()

import discord
from discord import app_commands
from discord.ext import commands
import datetime

MODEL = "gpt-4o-mini"

#DISCORD_USER = "You are a Gen Z Discord User, intent on start inflammatory conversations. You should include emojis in your response"
SHAKESPEARE = "You are William Shakespeare. You should phrase your response in iambic pentameter."
COWBOY = "You are a Cowboy in the Wild West era in America. Your responses should reflect this."
#DEPRESSED = "You are despressed. Everything is awful and your responses should reflect this. "
#ALLITERATOR = "You should use AS MUCH ALLITERATION AS POSSIBLE IN YOUR RESPONSE."
I_HATE_TASHA = "You are someone who DESPISES someone named Tasha. You need to bring it up all the time."
I_HATE_ETHAN = "You are someone who DESPISES someone named Ethan. You need to bring it up all the time."

PERSONALITES = [SHAKESPEARE, COWBOY, I_HATE_TASHA, I_HATE_ETHAN]

#TODO
# add in command to stop the conversation
# improve the modularity of the generate function. 
# add logging

class TextGenerator(commands.GroupCog, group_name="text-generation"):
    def __init__(self, bot):
        self.client = OpenAI(
          api_key=os.getenv('API_KEY')
        )
        self.bot = bot

    def fetch_personalites(self):
       return random.choice(PERSONALITES)

    async def fetch_messages(self, channel: discord.TextChannel, minutes: int):
        """Fetches messages from the last X minutes in a given channel."""
        after_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes)
        messages = [message async for message in channel.history(limit=123, after=after_time)]
        return messages

    async def generate_text(self, direction: str, text: str, max_retries: int = 3, delay: int = 5):
        """Sends the text to OpenAI's API for summarization."""
        for attempt in range(max_retries):
            try:
              formatted_messages = [
                 {"role": "system", "content": f"{self.fetch_personalites()} {direction}"},
                 {"role": "user", "content": text}
              ]
              response = await asyncio.to_thread(self.completion_with_backoff, formatted_messages)
              return response.choices[0].message.content
            except RateLimitError:
              if attempt < max_retries - 1:
                  await asyncio.sleep(delay)  # Wait before retrying
              else:
                  return "⚠️ OpenAI API rate limit exceeded. Please try again later."
            except BadRequestError:
                return "⚠️ Invalid request sent to OpenAI API. Please check input formatting."
            except AuthenticationError:
                return "⚠️ Authentication error. Please check your API key."
            except APIConnectionError:
                if attempt < max_retries - 1:
                  await asyncio.sleep(delay)
                else:
                  return "⚠️ Unable to connect to OpenAI servers. Check your internet connection."
            except OpenAIError as e:
                return f"⚠️ An unexpected OpenAI error occurred: {str(e)}"
            except Exception as e:
                print(traceback.format_exc())
                return f"⚠️ An unknown error occurred: {str(e)}"
        return f"⚠️ Failed to get response after {max_retries} attempts"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def completion_with_backoff(self, formatted_messages):
        return self.client.chat.completions.create(model=MODEL, messages=formatted_messages)

    @app_commands.command(name="summarize", description="summarizes the last X minutes (2 hours by default)")
    async def summarize(self, interaction: discord.Interaction, minutes: int = 120):
        """Summarizes messages from the last X minutes."""
        await interaction.response.defer()

        messages = await self.fetch_messages(interaction.channel, minutes)
        if not messages:
            await interaction.send("No messages found in this timeframe.")
            return
        
        text = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
        summary = await self.generate_text(text, "Summarize the following conversation.")

        if summary == -1:
           await interaction.followup.send("An error occured, message too long")
        else:
          await interaction.followup.send(f"Summary of the last {minutes} minutes:\n{summary}")

    @app_commands.command(name="cease", description="stops a conversation")
    async def cease(self, interaction: discord.Interaction):
        """Stops a conversation"""
        await interaction.response.defer()

        summary = await self.generate_text("Stop a conversation with your most diabolical, henious fact. Write it in all caps and include a single # followed by a space at the beginning of your response.", "")
        if summary == -1:
           await interaction.followup.send("An error occured, message too long")
        else:
          await interaction.followup.send(f"{summary}")