#!/usr/bin/python
from pulp import *
import csv
import numpy as np
import os

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

def create_premier_league():
    premier_teams = os.listdir('../data/Premier League Teams/')
    for file in premier_teams:
        premier_league_team = open('../data/Premier League Teams/'+ file,encoding='cp1252')
        reader = csv.reader(premier_league_team)
        next(reader)
        a = []
        selection = []

        for row in reader:
            a.append(row)
            selection.append(LpVariable("Player_"+str(row[0]),0,None,LpBinary))
        premier_league_team.close()
        a = np.array(a)
        overall = []
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
        
        overall = np.array(overall)
        is_goalkeeper = np.array(is_goalkeeper)
        is_defense = np.array(is_defense)
        is_midfield = np.array(is_midfield)
        is_offense = np.array(is_offense)

        # Begin Creating the Maximization Problem
        prob = LpProblem('Fifa Team', LpMaximize)

        ## Set the objective function
        # maximise skill
        total_skill = sum(x * obj for x,obj in zip(selection,overall))
        prob += total_skill,"Maximize Skill"
        
        prob = create_formation(prob,selection,1,is_goalkeeper,4,is_defense,4,is_midfield,2,is_offense)
        
        prob.solve()
        print(f"Team: {file} Status: {LpStatus[prob.status]}")
        print("Maximized Skill = ", value(prob.objective))
        for v in prob.variables():
            print(v.name, "=", v.varValue)

        print("\n\n\n")


def premier_disrupter():
    pass

def main():
    create_premier_league()

if __name__ == "__main__":
    main()