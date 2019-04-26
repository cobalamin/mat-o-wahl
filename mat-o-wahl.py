import json
import sys
import random
from math import exp

file = open("party.json", "r")
parties = json.load(file)
file.close()
if len(sys.argv) != 3:
    print("Gib mal genau 2 Parameter")
    exit()
id1 = id2 = -1
for x in parties:
    if x["name"] == sys.argv[1]:
        id1 = x["id"]
    if x ["name"] == sys.argv[2]:
        id2 = x["id"]
if id1 == -1 or id2 == -1 or id1 == id2:
    print("Ich kenne die Parteien nicht oder sie sind gleich")
    exit()
file = open("opinion.json", "r")
data = json.load(file)
file.close()
file = open("answer.json", "r")
answertext = json.load(file)
file.close()

def evaluateScore(opinion, answer):
    opval = opinion["answer"]
    if opval == answer:
        return 2
    # it is true iff one of them is 1 and the other 0
    if opval + answer == 1:
        return 0
    return 1
    

def evaluateOne(party, answers, double):
    total = score = 0
    poffset = 38*party["id"]
    for i in range(38):
        if answers[i] != -1:
            total += 2
            questionscore = evaluateScore(data[poffset+i], answers[i])
            if double[i]:
                questionscore *= 2
                total += 2
            score += questionscore
    return 0 if total == 0 else score/total

def energy(x):
    val = 0
    pos = 1000
    neg = 1000
    eq = 1500
    ev1 = evaluateOne(parties[id1], x[0], x[1])
    ev2 = evaluateOne(parties[id2], x[0], x[1])

    val -= pos * (ev1 + ev2) *100
    val += eq * abs(ev1-ev2) * 100
    m = 0
    for y in parties:
        if y["id"] != id1 and y["id"] != id2:
            m = max(m, evaluateOne(y, x[0], x[1]))
    val -= neg*m*100
    return val

def evaluateAll(answers, double):
    for x in parties:
        print(x["name"], evaluateOne(x, answers, double))

questnum = 38

steps = 100000
temperature = 100
kb = 0.001
deltatemp = temperature/steps

def print_pretty(x):
    for i in range(38):
        print(i+1, answertext[x[0][i]]["message"])
    for i in range(38):
        if x[1][i]:
            print(i+1)

def annealing():
    global temperature
    answer = [[1 for y in range(38)],[False for z in range(38)]]
    oldenergy = energy(answer)
    for _ in range(steps):
        #print(temperature)
        part = random.randint(0,1)
        index = random.randint(0,questnum-1)
        oldval = answer[part][index]
        if part == 0:
            x = [0,1,2]
            del(x[oldval])
            newval = random.choice(x)
        else:
            newval = not oldval
        answer[part][index] = newval
        newenergy = energy(answer)
        accept = newenergy < oldenergy or \
        random.random() <= exp(-1/(kb*temperature))

        if accept:
            oldenergy = newenergy
        else:
            answer[part][index] = oldval
        temperature -= deltatemp
    evaluateAll(answer[0], answer[1])
    print_pretty(answer)
annealing()