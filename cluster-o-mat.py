import json
import numpy as np
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy  import cophenet
from scipy.spatial.distance import pdist

f = open("opinion.json")
data = json.loads(f.read())
f.close()
f = open("party.json")
parties = json.loads(f.read())
f.close()
f = open("statement.json")
statements = json.loads(f.read())
f.close()
barlabels = [entry["label"] for entry in statements]

labels = [entry["name"] for entry in parties]
print(labels)
ansdict = {}

def show_plot(Z, labels):
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        Z,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=8.,  # font size for the x axis labels,
        labels=labels
    )
    plt.show()

def change_format(input):
    l = [1, -1, 0]
    return l[input]
    #return input
    

for entry in data:
    p = entry["party"]
    if p not in ansdict:
        ansdict[p] = np.zeros((38,), dtype=int)
    ansdict[p][entry["statement"]]= (change_format(entry["answer"]))

clusterdata = np.vstack((ansdict[0], ansdict[1]),)
for k in range(2, len(parties)):
    clusterdata = np.vstack((clusterdata, ansdict[k]),)
np.savetxt("fuck.txt", clusterdata, fmt="%d")
print(clusterdata.shape)
Z = linkage(clusterdata, 'ward')
c, coph_dists = cophenet(Z, pdist(clusterdata))

show_plot(Z, labels)

index = np.zeros(38, dtype=int)
res = np.zeros(38, dtype=float)
for i in range(38):
    res[i] = np.average(clusterdata[:,i])
    print(res[i])
    index[i] = i

plt.bar(index, res)
#plt.xticks(np.array(barlabels), rotation='vertical')
print(labels)
print(list(zip(labels, clusterdata[:,15].tolist())))
#plt.show()