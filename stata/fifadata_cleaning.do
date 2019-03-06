*******************************
**** CLEANING OF FIFA DATA ****
*******************************




*create log
log using "F:\fifa\stata\fifadata_cleaning.log", replace

*import data
use "F:\fifa\stata\fifadata_original.dta", clear




***********************************************************cleaning procedure

*create observation variable
drop v1
gen obs=[_n-1]
summarize obs

*get rid of $M and $K for dollar figures in variables
*value
gen value2=substr(value,-1,.)
tabulate value2
replace value=subinstr(value,"M","",.)
replace value=subinstr(value,"K","",.)
destring value, replace
gen value3=value*1000000 if value2=="M"
replace value3=value*1000 if value2=="K"
replace value3=0 if value==.
drop value value2
rename value3 value
summarize value
*wage
gen wage2=substr(wage,-1,.)
tabulate wage2
replace wage=subinstr(wage,"K","",.)
destring wage, replace
gen wage3=wage*1000 if wage2=="K"
replace wage3=0 if wage==.
drop wage wage2
rename wage3 wage
summarize wage
*releaseclause
gen releaseclause2=substr(releaseclause,-1,.)
tabulate releaseclause2
replace releaseclause=subinstr(releaseclause,"M","",.)
replace releaseclause=subinstr(releaseclause,"K","",.)
destring releaseclause, replace
gen releaseclause3=releaseclause*1000000 if releaseclause2=="M"
replace releaseclause3=releaseclause*1000 if releaseclause2=="K"
*blank values left as blank (no 0's in original)
drop releaseclause releaseclause2
rename releaseclause3 releaseclause
summarize releaseclause
*order them together
order id name age photo nationality flag overall potential club clublogo value wage releaseclause

****************
*match to Eric's
****************
drop if overall==0
drop if value==0
summarize overall
summarize value
summarize wage

*weight get rid of lbs
destring weight, replace ignore("lbs")
summarize weight

*add variables together
gen lsfinal=ls+ls2
drop ls ls2
rename lsfinal ls
summarize ls
gen stfinal=st+st2
drop st st2
rename stfinal st
summarize st
gen rsfinal=rs+rs2
drop rs rs2
rename rsfinal rs
summarize rs
gen lwfinal=lw+lw2
drop lw lw2
rename lwfinal lw
summarize lw
gen lffinal=lf+lf2
drop lf lf2
rename lffinal lf
summarize lf
gen cffinal=cf+cf2
drop cf cf2
rename cffinal cf
summarize cf
gen rffinal=rf+rf2
drop rf rf2
rename rffinal rf
summarize rf
gen rwfinal=rw+rw2
drop rw rw2
rename rwfinal rw
summarize rw
gen lamfinal=lam+lam2
drop lam lam2
rename lamfinal lam
summarize lam
gen camfinal=cam+cam2
drop cam cam2
rename camfinal cam
summarize cam
gen ramfinal=ram+ram2
drop ram ram2
rename ramfinal ram
summarize ram
gen lmfinal=lm+lm2
drop lm lm2
rename lmfinal lm
summarize lm
gen lcmfinal=lcm+lcm2
drop lcm lcm2
rename lcmfinal lcm
summarize lcm
gen cmfinal=cm+cm2
drop cm cm2
rename cmfinal cm
summarize cm
gen rcmfinal=rcm+rcm2
drop rcm rcm2
rename rcmfinal rcm
summarize rcm
gen rmfinal=rm+rm2
drop rm rm2
rename rmfinal rm
summarize rm
gen lwbfinal=lwb+lwb2
drop lwb lwb2
rename lwbfinal lwb
summarize lwb
gen ldmfinal=ldm+ldm2
drop ldm ldm2
rename ldmfinal ldm
summarize ldm
gen cdmfinal=cdm+cdm2
drop cdm cdm2
rename cdmfinal cdm
summarize cdm
gen rdmfinal=rdm+rdm2
drop rdm rdm2
rename rdmfinal rdm
summarize rdm
gen rwbfinal=rwb+rwb2
drop rwb rwb2
rename rwbfinal rwb
summarize rwb
gen lbfinal=lb+lb2
drop lb lb2
rename lbfinal lb
summarize lb
gen lcbfinal=lcb+lcb2
drop lcb lcb2
rename lcbfinal lcb
summarize lcb
gen cbfinal=cb+cb2
drop cb cb2
rename cbfinal cb
summarize cb
gen rcbfinal=rcb+rcb2
drop rcb rcb2
rename rcbfinal rcb
summarize rcb
gen rbfinal=rb+rb2
drop rb rb2
rename rbfinal rb
summarize rb




*save
save "F:\fifa\stata\fifadata_cleaned.dta", replace
export delimited "F:\fifa\stata\fifadata_cleaned.csv", replace




log close
exit, clear
