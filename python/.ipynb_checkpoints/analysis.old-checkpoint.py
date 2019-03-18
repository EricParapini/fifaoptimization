#!/usr/bin/python
import cvxpy as cp
import csv
import numpy as np

#	0	1	2		3	4		5			6		7		8			9		10	 11		12		13		14		15				16							17			18			19			20	21	22	23	24	25	26	27	28	29	30	31	32	33	34	35	36	37	38	39	40	41	42	43	44	45	46	47	48	49	50	51	52	53	54	55	56	57	58	59	60	61	62	63	64	65	66	67	68	69	70	71	72	73	74	75	76	77	78	79	80	81	82	83	84	85	86	87	88	89	90	91	92	93
# Num	ID	Name	Age	Photo	Nationality	Flag	Overall	Potential	Club	Club Logo	Value	Wage	Special	Preferred Foot	International Reputation	Weak Foot	Skill Moves	Work Rate	Body Type	Real Face	Position	Jersey Number	Joined	Loaned From	Contract Valid Until	Height	Weight	LS	ST	RS	LW	LF	CF	RF	RW	LAM	CAM	RAM	LM	LCM	CM	RCM	RM	LWB	LDM	CDM	RDM	RWB	LB	LCB	CB	RCB	RB	Crossing	Finishing	HeadingAccuracy	ShortPassing	Volleys	Dribbling	Curve	FKAccuracy	LongPassing	BallControl	Acceleration	SprintSpeed	Agility	Reactions	Balance	ShotPower	Jumping	Stamina	Strength	LongShots	Aggression	Interceptions	Positioning	Vision	Penalties	Composure	Marking	StandingTackle	SlidingTackle	GKDiving	GKHandling	GKKicking	GKPositioning	GKReflexes	Release Clause	PositionCode	Is_GK	Is_Defense	Is_Midfield	Is_Offense

fifa_data_file = open('../out/clean.csv',"r")
reader = csv.reader(fifa_data_file)
# Skip the header row
next(reader)
rownum = 0
a = []
for row in reader:
    a.append(row)
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
    overall.append(row[7])
    wage.append(row[12])
    is_goalkeeper.append(row[90])
    is_defense.append(row[91])
    is_midfield.append(row[92])
    is_offense.append(row[93])

# Convert all to NumpyArrays to save some space
overall = np.array(overall)
wage = np.array(wage)
is_goalkeeper = np.array(is_goalkeeper)
is_defense = np.array(is_defense)
is_midfield = np.array(is_midfield)
is_offense = np.array(is_offense)


# Create the selection variable
selection = cp.Variable(shape=len(overall),boolean=True)

## Set the objective function
# maximise skill
total_overall = overall * selection
constr1 = ( selection >= 5)
constr2 = ( selection <= 5)


## Create some limits
# Create a budget = 1M
budget = 1000000

fifa_team = cp.Problem(cp.Maximize(total_overall),[constr1,constr2])

fifa_team.solve(solver=cp.ECOS_BB)
print(f"Optimal Team Ability is {fifa_team.value} with a budget of {budget}")

print("Team Selection is:")
print(selection.value)
for x in selection:
    print (x.value)
