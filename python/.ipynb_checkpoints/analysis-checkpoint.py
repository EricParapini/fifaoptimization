#!/usr/bin/python
from pulp import *
import csv
import numpy as np

#	0	1	2		3	4		5			6		7		8			9		10	 11		12		13		14		15				16							17			18			19			20			21			22			23				24		25									26		27		28	29	30	31	32	33	34	35	36	37	38	39	40	41	42	43	44	45	46	47	48	49	50	51	52	53	54			55			56				57				58		59			60		61			62			63			64				65			66		67			68		69			70		71		72			73			74			75				76			77		78			79			80		81				82				83			84			85			86				87			88				89				90		91			92			93
# Num	ID	Name	Age	Photo	Nationality	Flag	Overall	Potential	Club	Club Logo	Value	Wage	Special	Preferred Foot	International Reputation	Weak Foot	Skill Moves	Work Rate	Body Type	Real Face	Position	Jersey Number	Joined	Loaned From	Contract Valid Until	Height	Weight	LS	ST	RS	LW	LF	CF	RF	RW	LAM	CAM	RAM	LM	LCM	CM	RCM	RM	LWB	LDM	CDM	RDM	RWB	LB	LCB	CB	RCB	RB	Crossing	Finishing	HeadingAccuracy	ShortPassing	Volleys	Dribbling	Curve	FKAccuracy	LongPassing	BallControl	Acceleration	SprintSpeed	Agility	Reactions	Balance	ShotPower	Jumping	Stamina	Strength	LongShots	Aggression	Interceptions	Positioning	Vision	Penalties	Composure	Marking	StandingTackle	SlidingTackle	GKDiving	GKHandling	GKKicking	GKPositioning	GKReflexes	Release Clause	PositionCode	Is_GK	Is_Defense	Is_Midfield	Is_Offense

fifa_data_file = open('../out/clean.csv',"r")
reader = csv.reader(fifa_data_file)
# Skip the header row
next(reader)
rownum = 0
a = []
selection = []
for row in reader:
    a.append(row)
    selection.append(LpVariable("Player_"+str(row[0]),0,None,LpBinary))
    rownum += 1
fifa_data_file.close()
a = np.array(a)

overall = []
wage = []
is_goalkeeper = []
is_defense = []
is_midfield = []
is_offense = []
# Populate the Constraint Matrices
for row in a:
    overall.append(int(float(row[7])))
    wage.append(int(float(row[12])))
    is_goalkeeper.append(int(float(row[90])))
    is_defense.append(int(float(row[91])))
    is_midfield.append(int(float(row[92])))
    is_offense.append(int(float(row[93])))

# Convert all to NumpyArrays to save some space
overall = np.array(overall)
wage = np.array(wage)
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

## Create some limits
# Create a budget = 1M
budget = 1000000
total_wage = sum(x * w for x,w in zip(selection,wage))
prob += total_wage <= budget

total_gk = sum(x * gk for x,gk in zip(selection,is_goalkeeper))
prob += total_gk == 1

total_defense = sum(x * defense for x,defense in zip(selection,is_defense))
prob += total_defense == 4

total_midfield = sum(x * mid for x,mid in zip(selection,is_midfield))
prob += total_midfield == 4

total_offense = sum(x * off for x,off in zip(selection,is_offense))
prob += total_offense == 2

prob.solve()
print("Status: ",LpStatus[prob.status])

for v in prob.variables():
    print(v.name, "=", v.varValue)

print("Maximized Skill = ", value(prob.objective))
