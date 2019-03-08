
clc;
clear all;
% load data
filename = 'clean2.csv';
M = csvread(filename,2,0)

[m,n] = size(M);

% optimization variables
x = binvar(m,1);

% objective
Objective = x'*M(:,1);

% Constraints
Constraints = [x'*M(:,2) <= 1000000; x >=0,x'* M(:,7) == 1,  x'* M(:,6) == 1,  x'* M(:,5) == 1];

% con = 0;
% for i = 1:1:m
%     if (M(i,3) == 4)
%         con = con + x(i);
%     end
% end
% 
% Constraints = [Constraints , con == 1]

% solves
optimize(Constraints,-Objective)

value(x)