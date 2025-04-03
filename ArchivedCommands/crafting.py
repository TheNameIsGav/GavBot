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
affinities = ["Abjuration", "Conjuration", "Divination", 
              "Enchantment", "Evocation", "Illusion", 
              "Transmutation", "Necrotic"]

def harvest(roll:int):
    distribution = 0

    if(roll <= distribution_thresholds[0]):
        distribution = 0
    elif(roll > distribution_thresholds[0] and roll <= distribution_thresholds[1]):
        distribution = 1
    elif(roll > distribution_thresholds[1] and roll <= distribution_thresholds[2]):
        distribution = 2
    elif(roll > distribution_thresholds[2] and roll <= distribution_thresholds[3]):
        distribution = 3
    else:
        distribution = 4
    chance_roll = random.randint(1, 100)
    target_harvest = harvest_chances[distribution]
    sum_harvest = 0
    j = 1
    for x in target_harvest:
        sum_harvest += x
        if(chance_roll <= sum_harvest):
            affinity = random.choice(affinities) if random.randint(1,100) <= 10 else None
            return j, affinity
        j += 1

def harvest_string(roll:int):
    (j, affinity) = harvest(roll)
    return f"{harvest_amounts[j-1]} Tier {j} reagent.", affinity

def normalize(val, new_min, new_max, old_min, old_max):
    return (((val - old_min) / (old_max - old_min)) * (new_max - new_min)) + new_min

def craft_chance(craft_skill:int, challenge_rating:int):
    #Craft skill is craft skill + d20 roll
    normalized_craft_skill = normalize(craft_skill, 0, 1, 0, 75)
    normalized_challenge_rating = normalize(challenge_rating, 0, 1, 1, 178)
    ratio = normalized_craft_skill / normalized_challenge_rating

    #Z is chance of success
    #E is chance of gaining experience

    if ratio > 1: #Craft Skill is greater than challenge rating, Z doesn't change and E decreases
        #As ratio gets further from 1, E decreases dramatically to a min of 0. 
        #Z remains constant. 
        return
    if ratio <= 1: #Craft skill is less than challenge rating, Z should increase as it gets closer to 1 
        #As ratio gets closer to 1, Z and E increases - at 1 E should be 100%, and Z should be 75%
        return
    print(ratio)

class Crafting(commands.GroupCog, group_name="crafting"):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        self._last_member = None
    
    @app_commands.command(name="harvest", description="Given a single number, harvest with that number")
    async def harvest(interaction: discord.Interaction, roll:int):
        """Rolls for harvesting

        Parameters
        -----------
        roll: int
            the roll to calculate
        """
        (j, affinity) = harvest_string(roll)
        print(affinity)
        await interaction.response.send_message(f"Harvested {j}" if affinity == None else 
            f"Harvested {j} Congratulations, your reagent has {affinity} affinity."
        )

def harvester_tester():

    all_combined_results = {}
    runs = 10000

    for x in [1,11,20,26,30]:
        run_results = [0,0,0,0,0]
        affinity_count = 0
        for y in range(0, runs):
            (result, affinity) = harvest(x)
            if(affinity): affinity_count += 1
            match result-1:
                case 0:
                    run_results[0] += 1
                case 1:
                    run_results[1] += 1
                case 2:
                    run_results[2] += 1
                case 3:
                    run_results[3] += 1
                case 4:
                    run_results[4] += 1
        all_combined_results[x] = run_results
        print(f"Over {runs} runs, harvested {affinity_count} reagents with affinities.")
    
    for x in all_combined_results:
        print(f"{x} {all_combined_results[x]}")