from utils import *
import random
import math
from discord.ext import commands
from discord import app_commands

distribution_thresholds = [10, 19, 25, 29]
harvest_chances = [[40, 30, 20, 5, 5],
                   [25, 40, 20, 10, 5],
                   [20, 25, 40, 10, 5],
                   [10, 25, 25, 30, 10],
                   [10, 15, 20, 35, 20]
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
        affinities = []
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

            if(roll_100 <= harvest_chances[distribution-1][4]):
                #tier 5
                tiers[4] += harvest_amounts[4]
                if(is_affinity): affinities.append(f"{harvest_amounts[4]} of Tier 5 {global_affinities[affinity]}")
            elif(roll_100 <= harvest_chances[distribution-1][3]):
                #tier 4
                tiers[3] += harvest_amounts[3]
                if(is_affinity): affinities.append(f"{harvest_amounts[3]} of Tier 4 {global_affinities[affinity]}")
            elif(roll_100 <= harvest_chances[distribution-1][2]):
                #tier 3
                tiers[2] += harvest_amounts[2]
                if(is_affinity): affinities.append(f"{harvest_amounts[2]} of Tier 3 {global_affinities[affinity]}")
            elif(roll_100 <= harvest_chances[distribution-1][1]):
                #tier 2
                tiers[1] += harvest_amounts[1]
                if(is_affinity): affinities.append(f"{harvest_amounts[1]} of Tier 2 {global_affinities[affinity]}")
            elif(roll_100 <= harvest_chances[distribution-1][0]):
                #tier 1
                tiers[0] += harvest_amounts[0]
                if(is_affinity): affinities.append(f"{harvest_amounts[0]} of Tier 1 {global_affinities[affinity]}")

            Log(f"""Attempt: {num}, 
Skill Roll: {roll}, 
Distribution: {distribution}, 
D100 Roll: {roll_100}
Affinity: {global_affinities[affinity] if is_affinity else ""}
Tiers: {tiers}
=============================""", loggerName="dnd_utils")

        return tiers, affinities

    
    @app_commands.command(
        name="bulk_havest", description="Simulates harvesting a large amount of resources with a distributed average"
    )
    async def bulk_harvest(self, interaction: discord.Interaction, attempts:int, skill:int):
        #Take in the skill in question, rely on the user to know what they're harvsting
        await interaction.response.defer()
        #Average out what we get and the affinites
        tiers, affinities = self.bulk_harvest_impl(attempts, skill)

        affinities_string = "\n".join(affinities)

        await interaction.followup.send(f"""
With {attempts} attempts and a +{skill} to your rolls, you found 
- {tiers[0]} Tier 1

- {tiers[1]} Tier 2

- {tiers[2]} Tier 3

- {tiers[3]} Tier 4

- {tiers[4]} Tier 5

Among those you get 
{affinities_string} 
(Raw count of affinities is included in tiers, do not double up please)""")