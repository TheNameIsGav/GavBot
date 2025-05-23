from utils import *
import random
import math
from discord.ext import commands
from discord import app_commands
from discord.errors import HTTPException

distribution_thresholds = [10, 19, 25, 29]
harvest_chances = [[100, 60, 30, 10, 5],
                   [100, 75, 35, 15, 5],
                   [100, 80, 55, 15, 5],
                   [100, 90, 65, 40, 10],
                   [100, 90, 75, 55, 20]
                   ]
harvest_amounts = [1, .75, .5, .25, .25]
global_affinities = ["Abjuration", "Conjuration", "Divination", 
              "Enchantment", "Evocation", "Illusion", 
              "Transmutation", "Necrotic"]

class DNDUtils(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    def bulk_harvest_impl(self, attempts, skill):
        Log("Rolling bulk harvester", loggerName="dnd_utils")

        tiers = [0,0,0,0,0]
        affinities = {"Abjuration" : [0,0,0,0,0],
                      "Conjuration" : [0,0,0,0,0],
                      "Divination" : [0,0,0,0,0],
                      "Enchantment" : [0,0,0,0,0],
                      "Evocation" : [0,0,0,0,0],
                      "Illusion" : [0,0,0,0,0],
                      "Transmutation" : [0,0,0,0,0],
                      "Necrotic" : [0,0,0,0,0]}
        for num in range(attempts):
            roll = random.randint(1, 20) + skill
            distribution = 0
            if(roll <= 10):
                distribution = 1
            elif(roll >= 11 and roll <= 19):
                distribution = 2
            elif(roll >= 20 and roll <= 25):
                distribution = 3
            elif(roll >= 26 and roll <=29):
                distribution = 4
            elif(roll >= 30):
                distribution = 5

            roll_100 = random.randint(1, 100)

            is_affinity = random.randint(1, 10) == 10
            affinity = random.randint(0, 7)
            school = global_affinities[affinity]

            if(roll_100 <= harvest_chances[distribution-1][4]):
                #tier 5
                if(is_affinity): affinities[school][4] += harvest_amounts[4]
                else: tiers[4] += harvest_amounts[4]
            elif(roll_100 <= harvest_chances[distribution-1][3]):
                #tier 4
                if(is_affinity): affinities[school][3] += harvest_amounts[3]
                else: tiers[3] += harvest_amounts[3]
            elif(roll_100 <= harvest_chances[distribution-1][2]):
                #tier 3
                if(is_affinity): affinities[school][2] += harvest_amounts[2]
                else: tiers[2] += harvest_amounts[2]
            elif(roll_100 <= harvest_chances[distribution-1][1]):
                #tier 2
                if(is_affinity): affinities[school][1] += harvest_amounts[1]
                else: tiers[1] += harvest_amounts[1]
            elif(roll_100 <= harvest_chances[distribution-1][0]):
                #tier 1
                if(is_affinity): affinities[school][0] += harvest_amounts[0]
                else: tiers[0] += harvest_amounts[0]

#             Log(f"""Attempt: {num}, 
# Skill Roll: {roll}, 
# Distribution: {distribution}, 
# D100 Roll: {roll_100}
# Affinity: {global_affinities[affinity] if is_affinity else ""}
# Tiers: {tiers}
# =============================""", loggerName="dnd_utils")

        return tiers, affinities

    
    @app_commands.command(
        name="bulk_havest", description="Simulates harvesting a large amount of resources"
    )
    async def bulk_harvest(self, interaction: discord.Interaction, attempts:int, skill:int, description:str = "None Provided"):
        try:
        #Take in the skill in question, rely on the user to know what they're harvsting
            await interaction.response.defer()
            #Average out what we get and the affinites
            tiers, affinities = self.bulk_harvest_impl(attempts, skill)
            affinities_string = ""
            for school in affinities.keys():
                affinities_string += f"""### {school} affinity 
{affinities[school][0]} Tier 1
{affinities[school][1]} Tier 2
{affinities[school][2]} Tier 3
{affinities[school][3]} Tier 4
{affinities[school][4]} Tier 5
"""
                
            if(len(affinities) == 0):
                affinities_string = "*hah no affinities for you loser*"

            await interaction.followup.send(f"""
Your description was: {description}
With {attempts} attempts and a +{skill} to your rolls, you found 
- {tiers[0]} Tier 1

- {tiers[1]} Tier 2

- {tiers[2]} Tier 3

- {tiers[3]} Tier 4

- {tiers[4]} Tier 5

Among those you get 
{affinities_string} """)
        except HTTPException as e:
            if e.status == 400:
                await interaction.followup.send("Reached character limit, try a lower # of attempts")
            else:
                await interaction.followup.send("An unknown error occured")