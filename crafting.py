from utils import *
import random

distribution_thresholds = [10, 19, 25, 29]
harvest_chances = [[40, 30, 20, 5, 5],
                   [25, 40, 20, 10, 5],
                   [20, 25, 40, 10, 5],
                   [10, 25, 25, 30, 10],
                   [10, 15, 20, 35, 20]
                   ]
harvest_amounts = [1, .75, .5, .25, .25]

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
            return j
        j += 1

def harvest_string(roll:int):
    j = harvest(roll)
    return f"{harvest_amounts[j-1]} Tier {j} reagent."

def harvest_many(roll:int, times:int=1):
    if(times == 1):
        j = harvest(roll)
        return f"Tier {j}: {harvest_amounts[j-1]}"

    for x in range(0, times):
        harvest(roll)

def harvester_tester():

    all_combined_results = {}

    for x in [1,11,20,26,30]:
        run_results = [0,0,0,0,0]
        for y in range(0, 10000):
            result = harvest(x)
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
    
    for x in all_combined_results:
        print(f"{x} {all_combined_results[x]}")