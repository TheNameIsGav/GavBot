import discord
from discord import app_commands
from discord.ext import commands
import os
from github import Github, GithubException, BadCredentialsException, InputGitAuthor

class GitHubFileEditor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.github_token = os.getenv('GITHUBPAT')
        self.repo_owner = os.getenv('GITHUBOWNER')
        self.repo_name = os.getenv('GITHUBREPO')
        self.repo_branch = "main"
        self.file_path = "GavBotWrites.md"  # Set this to the file you always want to edit

    @app_commands.command(name="append_to_file", description="Append text to a predefined GitHub file.")
    @commands.is_owner()
    async def append_to_file(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer(thinking=True)

        try:
            # Authenticate GitHub
            g = Github(self.github_token)

            # Get repo
            try:
                repo = g.get_repo(f"{self.repo_owner}/{self.repo_name}")
            except GithubException as e:
                return await interaction.followup.send(f"🚨 Failed to access repo `{self.repo_owner}/{self.repo_name}`: {e.data.get('message', 'Unknown error')}")

            # Fetch file
            try:
                file_content = repo.get_contents(self.file_path, ref=self.repo_branch)
            except GithubException as e:
                return await interaction.followup.send(f"🚨 Failed to fetch file `{self.file_path}`: {e.data.get('message', 'Unknown error')}")

            # Prepare updated content
            updated_content = file_content.decoded_content.decode('utf-8').rstrip('\n') + f"\n{text}\n"

            # Commit back
            try:
                commit_message = f"Appended via Discord bot"
                author = InputGitAuthor("Discord Bot", "GavBot")
                repo.update_file(self.file_path, commit_message, updated_content, file_content.sha, branch=self.repo_branch, author=author)
                await interaction.followup.send("✅ Successfully updated the file!")
            except GithubException as e:
                return await interaction.followup.send(f"🚨 Failed to update file: {e.data.get('message', 'Unknown error')}")

        except Exception as e:
            # Catch any other unhandled errors
            await interaction.followup.send(f"❗ Unexpected error occurred: {e}")