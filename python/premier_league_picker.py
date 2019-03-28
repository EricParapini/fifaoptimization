#!/usr/bin/python
import os
import multiprocessing
from pulp import *
import csv
import numpy as np
import random
import pandas as pd
from optparse import OptionParser
from itertools import permutations

# Create some arguments to make script more flexible - can now specify whether we want a full team refresh (time intensive)
def define_option_parser():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-r","--refresh",action="store_true",dest="refresh_disrupters",help="Specify whether the teams should be done")
    parser.add_option("-s","--seasons",type="int",dest="seasons",help="Set how many seasons to simulate",default=1)
    return parser

# Solver Debugging
def output_solver_results(name,prob):
    for v in prob.variables():
        name_id_split = v.name.split('_')
        print(name,",",name_id_split[0],",",name_id_split[1],",",v.varValue)

# Setup the initial binary variables and base player array
def setup_selection_a(path,encoding):
    opened_csv = open(path,encoding=encoding)
    reader = csv.reader(opened_csv)
    next(reader)
    a = []
    selection = []
    for row in reader:
        a.append(row)
        selection.append(LpVariable("Player_"+str(row[0]),0,None,LpBinary))
    opened_csv.close()
    return np.array(a), np.array(selection)

# Create the generic constraints for the problem, include the wage if specified
def create_generic_constraint_arrays(a,is_disrupter):
    overall = []
    wage = []
    is_goalkeeper = []
    is_defense = []
    is_midfield = []
    is_offense = []
    is_from_england = []

    # Populate the Constraint Matrices
    for row in a:
        overall.append(int(float(row[7])))
        is_goalkeeper.append(int(float(row[90])))
        is_defense.append(int(float(row[91])))
        is_midfield.append(int(float(row[92])))
        is_offense.append(int(float(row[93])))
        if is_disrupter:
            wage.append(int(float(row[12])))
            is_from_england.append(int(float(row[94])))


    if is_disrupter:
        return np.array(overall), np.array(wage), np.array(is_goalkeeper), np.array(is_defense), np.array(is_midfield), np.array(is_offense), np.array(is_from_england)
    return np.array(overall), np.array(is_goalkeeper), np.array(is_defense), np.array(is_midfield), np.array(is_offense)

# Allows for more dynamic formation constraint setting
def create_formation(prob,selection,gk_count,gk_array,def_count,def_array,mid_count,mid_array,off_count,off_array):
    total_gk = sum(x * gk for x,gk in zip(selection,gk_array))
    prob += total_gk == gk_count
    total_defense = sum(x * defense for x,defense in zip(selection,def_array))
    prob += total_defense == def_count
    total_midfield = sum(x * mid for x,mid in zip(selection,mid_array))
    prob += total_midfield == mid_count
    total_offense = sum(x * off for x,off in zip(selection,off_array))
    prob += total_offense == off_count
    return prob

# Specify the distribution of the team - how min values for GK, Defense, Mid, Offense, and max team size 
def team_distribution(prob,selection,min_gk_count,gk_array,min_def_count,def_array,min_mid_count,mid_array,min_off_count,off_array,max_team_size):
    total_gk = sum(x * gk for x,gk in zip(selection,gk_array))
    prob += total_gk >= min_gk_count
    total_defense = sum(x * defense for x,defense in zip(selection,def_array))
    prob += total_defense >= min_def_count
    total_midfield = sum(x * mid for x,mid in zip(selection,mid_array))
    prob += total_midfield >= min_mid_count
    total_offense = sum(x * off for x,off in zip(selection,off_array))
    prob += total_offense >= min_off_count
    total_players = sum(x for x in selection)
    prob += total_players <= max_team_size
    return prob

# Create the competition - iterate through premier league rosters and setup their team formations which maximized ability
def create_premier_league(formation_list):
    premier_teams = os.listdir('../data/Premier League Teams/')
    premier_team_return = []
    for file in premier_teams:
        a, selection = setup_selection_a('../data/Premier League Teams/'+ file,'utf8')
        overall, is_goalkeeper, is_defense, is_midfield, is_offense = create_generic_constraint_arrays(a,False)
        # Begin Creating the Maximization Problem
        prob = LpProblem('Fifa Team', LpMaximize)
        ## Set the objective function
        # maximise skill
        total_skill = sum(x * obj for x,obj in zip(selection,overall))
        prob += total_skill,"Maximize Skill"
        prob = create_formation(prob,selection,1,is_goalkeeper,formation_list[0],is_defense,formation_list[1],is_midfield,formation_list[2],is_offense)
        prob.solve()
        premier_team_return.append([file,prob,formation_list])
    return premier_team_return

# Create a new entrant to the premier league based on a max budget as the constraint
def create_premier_disrupter(max_budget):
    min_from_england = 8
    a, selection = setup_selection_a('../data/butpremier.csv','utf8')
    overall, wage, is_goalkeeper, is_defense, is_midfield, is_offense, from_england = create_generic_constraint_arrays(a,True)
    prob = LpProblem('Fifa Team', LpMaximize)
    ## Set the objective function
    # maximise skill
    total_skill = sum(x * obj for x,obj in zip(selection,overall))
    prob += total_skill,"Maximize Skill"
    # Specify team distribution
    prob = team_distribution(prob,selection,3,is_goalkeeper,10,is_defense,10,is_midfield,5,is_offense,33)
    # Stop picking too many goalies
    sum_of_gk = sum(x * gk for x,gk in zip(selection,is_goalkeeper))
    prob += sum_of_gk <= 3
    # Use the wage specification
    total_wage = sum(x * w for x,w in zip(selection,wage))
    prob += total_wage <= max_budget
    # Use the from_england specification
    total_from_england = sum(x * fe for x,fe in zip(selection,from_england))
    prob += total_from_england >= min_from_england
    prob.solve()
    # Write the resulting team to a simplified csv
    player_ids = []
    for v in prob.variables():
        if v.varValue == 1:
            name_id_split = v.name.split('_')
            player_ids.append(name_id_split[1])

    write_new_player_file(max_budget,player_ids)
    return [max_budget,prob]

# Create team outputs for the disruptive teams based on the pased in player ID's and the team budget
def write_new_player_file(budget,player_ids):
    df = pd.read_csv("../data/clean.csv")
    df.loc[df['Num'].isin(player_ids)].to_csv(r"../out/disrupter/disrupter_"+str(budget)+".csv", index=None, header=True)

# Reuse the formation optimization problem in earlier results
def create_disrupter_formation(formation_list):
    disruption_teams = os.listdir('../out/disrupter/')
    disrupter_team_return = []
    for file in disruption_teams:
        a, selection = setup_selection_a('../out/disrupter/'+ file,'utf8')
        overall, is_goalkeeper, is_defense, is_midfield, is_offense = create_generic_constraint_arrays(a,False)
        # Begin Creating the Maximization Problem
        prob = LpProblem('Fifa Team', LpMaximize)
        ## Set the objective function
        # maximise skill
        total_skill = sum(x * obj for x,obj in zip(selection,overall))
        prob += total_skill,"Maximize Skill"
        prob = create_formation(prob,selection,1,is_goalkeeper,formation_list[0],is_defense,formation_list[1],is_midfield,formation_list[2],is_offense)
        prob.solve()
        disrupter_team_return.append([file,value(prob.objective),formation_list])
    return disrupter_team_return

# Load the distribution spread from a file and create a dictionary to compare against
def load_spread():
    # Open the spreads file
    opened_csv = open('./res/distribution.csv',encoding='utf8')
    reader = csv.reader(opened_csv)
    next(reader)
    modifier_row = next(reader)    
    spread_dict = {int(float(x[0])) : [float(x[1]),float(x[2]),float(x[3])] for x in reader}
    # E.g., spread_dict[diff][List with spread] = Win for specified difference
    return spread_dict, modifier_row[0]

def create_premier_team_dict(premier_teams):
    premier_team_names = []
    premier_teams_dict = {}
    # Create Premier team dictionary
    for row in premier_teams:
        for team in row:
            premier_team_names.append(team[0][:-4])
            key = team[0][:-4]
            key += ''.join(map(str,team[2]))
            premier_teams_dict.update({key : (value(team[1].objective)/11)})
    premier_team_names = list(dict.fromkeys(premier_team_names))
    return premier_team_names, premier_teams_dict

def create_disrupter_team_dict(disrupter_teams):
    disrupter_team_dict = {}
    for row in disrupter_teams:
    # Team[0] file Team[1] = overall Team[2]=formation
        for team in row:
            key = (team[0].split('_')[1][:-4])+"_"+(''.join(map(str,team[2])))
            avg_overall = (team[1]/11)
            disrupter_team_dict.update({key : avg_overall})
    return disrupter_team_dict

def constrain_diff(diff):
    if diff > 10:
        return 10
    if diff < -10:
        return -10
    return diff

def create_outcome_list(outcomes,spread_with_diff):
    game_outcome = np.random.choice(outcomes,p=spread_with_diff)
    if game_outcome == 'W':
        return ['0','0','1']
    if game_outcome == 'D':
        return ['0','1','0']
    if game_outcome == 'L':
        return ['1','0','0']
    return ['0','0','0']


# Seasons are simulated by having each team play each other twice (once home and once away)
def simulate_league(premier_teams,disrupter_teams,formations,budgets,seasons_to_simulate):
    # Fix the multiple wrappings
    formations = formations[0]
    ## Create the probability dictionary
    # Print the prob of a tie when diff is -3
    # print (spread_dict[-3][1])
    spread, modifier = load_spread()
    # Create the premier teams dictionary
    premier_team_names, premier_teams_dict = create_premier_team_dict(premier_teams)
    ## Create disrupter team dictionary
    # key = budget_formation : value = avg(overall)
    disrupter_team_dict = create_disrupter_team_dict(disrupter_teams)
    outcomes = ['L','D','W']
    print("Budget,Season,Home,Away,Loss,Draw,Win")
    for budget in budgets:
        disrupter_name = "Fundamentals F.C."
        for season in range(seasons_to_simulate):
            season += 1
            for team in premier_teams_dict:
                diff = constrain_diff(int(round(premier_teams_dict[team] - disrupter_team_dict[str(budget)+'_'+''.join(map(str,formations))],0)))
                outcome_list = ','.join(create_outcome_list(outcomes,spread[diff]))
                print (f"{budget},{season},{team[:-3]},{disrupter_name},{outcome_list}")
                diff = constrain_diff(int(round(disrupter_team_dict[str(budget)+'_'+''.join(map(str,formations))] - premier_teams_dict[team],0)))
                outcome_list = ','.join(create_outcome_list(outcomes,spread[diff]))
                print (f"{budget},{season},{disrupter_name},{team[:-3]},{outcome_list}")
            # Simulate the rest of the league
            season_schedule = permutations(premier_teams_dict.keys(),2)
            for game in season_schedule:
                # game[0] = team home 
                # game[1] = team away
                diff = constrain_diff(int(round(premier_teams_dict[game[0]] - premier_teams_dict[game[1]])))
                outcome_list = ','.join(create_outcome_list(outcomes,spread[diff]))
                print (f"{budget},{season},{game[0][:-3]},{game[1][:-3]},{outcome_list}")


def main():
    # Parse options passed in - easier to toggle full team refresh or not
    parser = define_option_parser()
    (options, args) = parser.parse_args()
    # Set an array of budgets to cover
    budgets = [250000,500000,750000,1000000,1250000,1500000,1750000,2000000,2250000,2500000,2750000,3000000]
    # Set an array of formations to cover
    formations = [[4,4,2]]
    ## Perform in parallel - my computer has 6 cores. On my computer each process takes ~ 400MB of RAM
    pool = multiprocessing.Pool(processes=6)
    # Create different formations for the premier teams
    premier_teams = pool.map(create_premier_league, formations)
    # Specify whether the new entrants will be 
    if options.refresh_disrupters:
        print("Refreshing Teams")
        pool.map(create_premier_disrupter, budgets)
    disrupter_teams = pool.map(create_disrupter_formation, formations)
    simulate_league(premier_teams,disrupter_teams,formations,budgets,options.seasons)

if __name__ == "__main__":
    main()