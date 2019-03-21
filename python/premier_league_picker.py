#!/usr/bin/python
import os
import multiprocessing
from pulp import *
import csv
import numpy as np
import random
import pandas as pd

def output_solver_results(name,prob):
    for v in prob.variables():
        name_id_split = v.name.split('_')
        print(name,"\t",name_id_split[0],"\t",name_id_split[1],"\t",v.varValue)

def dist_creation():
    # Example of weighted random variables - useful for L/D/W
    opened_csv = open('./distribution.csv',encoding='cp1252')
    reader = csv.reader(opened_csv)
    next(reader)
    dist = []
    for row in reader:
        dist.append(row)
    return dist

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

def main():
    budgets = [1500000,1750000,2000000,2250000,2500000]
    formations = [[4,4,2],[3,4,3],[4,3,3],[3,5,2]]
    ## Perform in parallel
    pool = multiprocessing.Pool(processes=12)
    premier_teams = pool.map(create_premier_league, formations)
    #new_teams = pool.map(create_premier_disrupter, budgets)
    disrupter_teams = pool.map(create_disrupter_formation, formations)

if __name__ == "__main__":
    main()