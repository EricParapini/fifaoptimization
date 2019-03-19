#!/usr/bin/python
import os
from multiprocessing import Process
from pulp import *
import csv
import numpy as np
import os

def create_distribution():
    return 1

def output_solver_results(file,prob):
    print(f"Team: {file} Status: {LpStatus[prob.status]}")
    print("Maximized Skill = ", value(prob.objective))
    for v in prob.variables():
        print(v.name, "=", v.varValue)
    print("\n\n\n")

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
def create_generic_constraint_arrays(a,with_wage):
    overall = []
    wage = []
    is_goalkeeper = []
    is_defense = []
    is_midfield = []
    is_offense = []

    # Populate the Constraint Matrices
    for row in a:
        overall.append(int(float(row[7])))
        is_goalkeeper.append(int(float(row[90])))
        is_defense.append(int(float(row[91])))
        is_midfield.append(int(float(row[92])))
        is_offense.append(int(float(row[93])))
        if with_wage:
            wage.append(int(float(row[12])))

    if with_wage:
        return np.array(overall), np.array(wage), np.array(is_goalkeeper), np.array(is_defense), np.array(is_midfield), np.array(is_offense)
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

def team_distribution(prob,selection,min_gk_count,gk_array,min_def_count,def_array,min_mid_count,mid_array,min_off_count,off_array):
    total_gk = sum(x * gk for x,gk in zip(selection,gk_array))
    prob += total_gk >= min_gk_count
    total_defense = sum(x * defense for x,defense in zip(selection,def_array))
    prob += total_defense >= min_def_count
    total_midfield = sum(x * mid for x,mid in zip(selection,mid_array))
    prob += total_midfield >= min_mid_count
    total_offense = sum(x * off for x,off in zip(selection,off_array))
    prob += total_offense >= min_off_count
    return prob

def create_premier_league():
    premier_teams = os.listdir('../data/Premier League Teams/')
    for file in premier_teams:
        a, selection = setup_selection_a('../data/Premier League Teams/'+ file,'cp1252')
        overall, is_goalkeeper, is_defense, is_midfield, is_offense = create_generic_constraint_arrays(a,False)
        
        # Begin Creating the Maximization Problem
        prob = LpProblem('Fifa Team', LpMaximize)

        ## Set the objective function
        # maximise skill
        total_skill = sum(x * obj for x,obj in zip(selection,overall))
        prob += total_skill,"Maximize Skill"
        
        prob = create_formation(prob,selection,1,is_goalkeeper,4,is_defense,4,is_midfield,2,is_offense)
        
        prob.solve()
        output_solver_results(file,prob)


def create_premier_disrupter(budget):
    print(f"Team with budget of {budget} under calculation by process{os.getpid()}")
    a, selection = setup_selection_a('../data/ButPremier.csv','cp1252')
    overall, wage, is_goalkeeper, is_defense, is_midfield, is_offense = create_generic_constraint_arrays(a,True)
    prob = LpProblem('Fifa Team', LpMaximize)
    ## Set the objective function
    # maximise skill
    total_skill = sum(x * obj for x,obj in zip(selection,overall))
    prob += total_skill,"Maximize Skill"
    # Specify team distribution
    prob = team_distribution(prob,selection,3,is_goalkeeper,10,is_defense,10,is_midfield,5,is_offense)
    # Use the wage specification
    total_wage = sum(x * w for x,w in zip(selection,wage))
    prob += total_wage <= budget
    prob.solve()
    print(f"Disrupter with budget of {budget}")
    output_solver_results('Disrupter',prob)



def main():
    dist = create_distribution()
    #create_premier_league()
    
    #Make multiprocessed
    budgets = [1500000,1750000,2000000,2250000,2500000]
    procs = []
    for budget in budgets:
        proc = Process(target=create_premier_disrupter,args=(budget,))
        procs.append(proc)
        proc.start()
    
    for proc in procs:
        proc.join()

if __name__ == "__main__":
    main()