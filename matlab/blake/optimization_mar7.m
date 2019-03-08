%load data
filename = 'fifa_mar7.csv';
M = csvread(filename,1,0);

%matrix
[m,n] = size(M)

%optimization variables
x = binvar(m,1);

%objective
Objective = x'*M(:,1);

%constraints
    %wage
Constraints = [x'*M(:,2) <= 1000000; x>=0];
    %goalie
Constraints = [Constraints, x'* M(:,4) == 1];
    %defence
Constraints = [Constraints, x'* M(:,5) == 4];
    %midfield
Constraints = [Constraints, x'* M(:,6) == 4];
    %offence
Constraints = [Constraints, x'* M(:,7) == 2];

%colve
optimize(Constraints,-Objective)

%values
diary fifa_mar7.out
value(x)
diary off
