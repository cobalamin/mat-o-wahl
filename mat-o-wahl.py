import json
import sys
import random
import copy
from optparse import OptionParser
from math import exp
import matplotlib.pyplot as plt

usage = "usage: %prog <party1> <party2> [options]"
parser = OptionParser()
parser.add_option("-i", "--id", dest="id", help="the election to analyze \
by id from \"wahl-o-mat-data/election.json\". The default is the \
id of the most recent election in Germany", type = "int",)
parser.add_option("-y", "--year", dest="year", help="the year you are \
interested in as yyyy format. If this option is set, the program will display \
all elections in the given year and their id", type="int")
parser.add_option("-p", "--parties", dest="parties", help="displays all parties\
 for election id and exits", action = "store_true", default = False)
parser.add_option("-s", "--show-plots", dest = "plot",  action="store_true", \
 default = False, help = "show energy and acceptance probability plot. This \
is useful to determine the simulation parameters")

(options, args) = parser.parse_args()
with open("wahl-o-mat-data/election.json") as el_json:
    elections = json.load(el_json)

if options.year is not None:
    if options.year < 1000:
        print("A year must be in the yyyy format (ie. 2016)" )
        exit()
    yearstr = str(options.year)
    print("Elections in "+yearstr)
    for election in elections:
        if election["date"][:4] == yearstr:
            #TODO format string
            print(election["name"]+": id = "+str(election["id"])+ ", Date: "\
            + election["date"])
    exit()

election_id = options.id
if election_id is None:
    election_id = len(elections) -1

basepath = "wahl-o-mat-data/"+ elections[election_id]["path"]

with open(basepath+"/party.json") as party_file:
    parties = json.load(party_file)

if options.parties:
    partynames = [party["name"] for party in parties]
    partystr = ""
    for name in partynames:
        partystr += name +", "
    print("Valid parties for " + elections[election_id]["name"]+ " are:")
    print(partystr[:-2])
    exit()

if len(args) != 2:
    print("2 parties are required.")
    print("Use -p to display valid parties for this election.")
    exit()
id1 = id2 = -1
haserr = False
for x in parties:
    if x["name"] == args[0]:
        id1 = x["id"]
    if x ["name"] == args[1]:
        id2 = x["id"]
if id1 == -1:
    print(args[0] + " is not a valid party for this election.")
    haserr = True
if id2 == -1:
    print(args[1] + " is not a valid party for this election.")
    haserr = True
if id1 != -1 and id1 == id2:
    print("The parties must be different.")
    haserr = True

if haserr:
    print("Use -p to display valid parties for this election.")
    exit()

with  open(basepath+"/answer.json") as ans_file:
    answertext = json.load(ans_file)

with open(basepath+"/opinion.json") as op_file:
    data = json.load(op_file)

with open(basepath+"/statement.json") as st_file:
    statements = json.load(st_file)

questnum = len(statements)

def evaluateScore(opinion, answer):
    opval = opinion["answer"]
    if opval == answer:
        return 2
    # it is true iff one of them is 1 and the other 0
    if opval + answer == 1:
        return 0
    return 1
    
# this is how the wahl-o-mat computes approval
def evaluateOne(party, answers, double):
    total = score = 0
    poffset = questnum*party["id"]
    for i in range(questnum):
        if answers[i] != -1:
            total += 2
            questionscore = evaluateScore(data[poffset+i], answers[i])
            if double[i]:
                questionscore *= 2
                total += 2
            score += questionscore
    return 0 if total == 0 else score/total

# Other ways of calculating energy are possible but high energies should 
# correspond to bad results and low energy should correspond to good
# results since the algorithm is minimizing the energy
def energy(x):
    # These parameters are basically magic numbers, with which results are the 
    # way I want them to be (ie. maximal values, 
    # equal values, a maximal gap between the two parties and the rest
    pos = 45
    neg = 20
    eq = 40

    val = 0
    ev1 = evaluateOne(parties[id1], x[0], x[1])
    ev2 = evaluateOne(parties[id2], x[0], x[1])

    val -= pos * (ev1 + ev2) *100
    val += eq * abs(ev1-ev2) * 100
    m = 0
    for y in parties:
        if y["id"] != id1 and y["id"] != id2:
            m = max(m, evaluateOne(y, x[0], x[1]))
    val += neg*m*len(parties)
    return val

def evaluateAll(answers, double):
    for x in parties:
        print(x["name"], evaluateOne(x, answers, double))

def print_pretty(x):
    for i in range(38):
        print(i+1, answertext[x[0][i]]["message"])
    for i in range(38):
        if x[1][i]:
            print(i+1)

def annealing():

    # Some simulation parameters, experiment with them as well to find the best
    # results
    steps = 10000
    temperature = 5
    deltatemp = temperature/(steps)

    energies = [ 0 for _ in range(steps)]
    ps = [ 0 for _ in range(steps)]

    xbest = []
    count = 0
    answer = [[random.randint(0,1) for y in range(questnum)], \
            [bool(random.randint(0,1)) for z in range(questnum)]]
    oldenergy = energy(answer)
    for i in range(steps):
        # change current answer a little bit
        part = random.randint(0,1)
        index = random.randint(0,questnum-1)
        oldval = answer[part][index]
        if part == 0:
            newval = random.randint(0,1)
            if newval >= oldval:
                newval += 1
        else:
            newval = not oldval
        answer[part][index] = newval

        # calculate whether the new answer is better or worse
        # and decide what to do based on energy/probability
        newenergy = energy(answer)
        if newenergy <= oldenergy:
            xbest = copy.deepcopy(answer)
            # Should be one but looks better in the plot lol
            ps[i] = 0
        else:
            ps[i] = exp(-(newenergy-oldenergy)/(temperature))
        accept = newenergy <= oldenergy or \
        random.random() <= ps[i]
        if accept:
            oldenergy = newenergy
            count += 1
        else:
            answer[part][index] = oldval

        # update simulation parameters
        temperature -= deltatemp
        energies[i] = oldenergy

    # Print results and show plot
    print("Result found after " + str(steps) + " steps and "\
    + str(count) + " swaps: \n")
    evaluateAll(xbest[0], xbest[1])
    print_pretty(xbest)

    if options.plot:
        plt.plot(energies)
        plt.figure()
        plt.plot(ps)
        plt.show()

annealing()