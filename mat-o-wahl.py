import json
import sys
import random

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

def fittness(x):
    val = 0
    pos = 800
    neg = 22
    eq = 1300
    ev1 = evaluateOne(parties[id1], x[0], x[1])
    ev2 = evaluateOne(parties[id2], x[0], x[1])
    val += pos * (ev1 + ev2) *100
    val -= eq * abs(ev1-ev2) * 100
    for y in parties:
        if y["id"] != id1 and y["id"] != id2:
            val -= neg*100* evaluateOne(y, x[0], x[1])
    return val

def evaluateAll(answers, double):
    for x in parties:
        print(x["name"], evaluateOne(x, answers, double))

poolsize = 100
mutrate = 0.12
gennum = 500

def mutate(x):
    for i in range(38):
        if random.uniform(0,1) <= mutrate:
            l = [0,1,2]
            l.remove(x[0][i])
            x[0][i] = random.choice(l)
        if random.uniform(0,1) <= mutrate:
            x[1][i] = not x[1][i]
    return x

def replicate(x, y):
    ans = []
    doub = []
    for i in range(38):
        if bool(random.getrandbits(1)):
            ans.append(x[0][i])
        else:
            ans.append(y[0][i])
        if bool(random.getrandbits(1)):
            doub.append(x[1][i])
        else:
            doub.append([y[1][i]])
    
    return mutate([ans, doub])

def print_pretty(x):
    for i in range(38):
        print(i+1, answertext[x[0][i]]["message"])
    for i in range(38):
        if x[1][i]:
            print(i+1)

def genetic():
    pool = [  [[1 for y in range(38)],[False for z in range(38)]] for _ in range(poolsize)]

    for i in range(gennum):
        print(i)
        pool.sort(key = fittness, reverse = True)
        for x in pool[0:10]:
            for y in pool[0:10]:
                pool.append(replicate(x,y))
        pool.sort(key = fittness, reverse = True)
        pool = pool[0:poolsize]

    pool.sort(key = fittness)
    evaluateAll(pool[0][0], pool[0][1])
    print_pretty(pool[0])

genetic()