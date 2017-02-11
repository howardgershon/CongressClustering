from lxml import html
from lxml import etree
import requests
from sklearn import cluster, datasets
import numpy as np
import pandas as pd
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
from matplotlib import pylab

# a function to get the bill numbers
def get_bills(n):
    page = requests.get('https://www.govtrack.us/data/us/'+n+'/bills/')
    tree = html.fromstring(page.content)
    bills = tree.xpath('//a/text()')
    bills = bills[1:]
    bill_nos = list(map(lambda x:x.split('.xml')[0], bills))
    return bill_nos
# a function to get the legislators
def get_legis(n, s):
    if (n == 114):
        legurl = 'https://www.govtrack.us/data/us/people.xml'
    else:
        legurl = 'https://www.govtrack.us/data/us/'+str(n)+'/people.xml'
    page = requests.get(legurl)
    root = etree.fromstring(page.content)
    peeps = []
    for r in root:
        role = r.getchildren()[0].get('type')
        id = r.get('id')
        if (role == s):
            peeps.append(int(id))
    #legis = tree.xpath
    return peeps

# a function to return the legislators role (rep or sen)
def get_role(id,yr):
    if (yr == 114):
        legurl = 'https://www.govtrack.us/data/us/people.xml'
    else:
        legurl = 'https://www.govtrack.us/data/us/'+str(yr)+'/people.xml'
    page = requests.get(legurl)
    root = etree.fromstring(page.content)
    for r in root:
        num = r.get('id')
        role = r.getchildren()[0].get('type')
        if(num == id):
            return role

# a function to get the party of a single congressperson
def get_party_single(id, yr):
    if (yr == 114):
        legurl = 'https://www.govtrack.us/data/us/people.xml'
    else:
        legurl = 'https://www.govtrack.us/data/us/'+str(yr)+'/people.xml'
    page = requests.get(legurl)
    root = etree.fromstring(page.content)
    party = []
    for r in root:
        num = r.get('id')
        if (id == num):
            return r.getchildren()[0].get('party')

# a function to return the parties of all the congress people
# in the same order as get_legis output
def get_party(yr,s):
    if (yr == 114):
        legurl = 'https://www.govtrack.us/data/us/people.xml'
    else:
        legurl = 'https://www.govtrack.us/data/us/'+str(yr)+'/people.xml'
    page = requests.get(legurl)
    root = etree.fromstring(page.content)
    party = []
    for r in root:
        role = r.getchildren()[0].get('type')
        if (role == s):
            party.append(r.getchildren()[0].get('party'))
    return party

# get the parties of the 113th congress
parties = get_party(113, 'rep')

# set the colors as red and blue
# this works because all of the congress people were republican or democrat
# otherwise this would have needed to be a little more complicated
colorparties = ['red' if x == 'Republican' else 'blue' for x in parties]

# use pandas to load the data
df = pd.DataFrame()
# I have left it commented out so it doesn't run
#df = df.from_csv('~/Google Drive/Fall 2016/CS2021/project/data113.csv')

# subset the adjacency matrix to only include the members of the house of
# representatives
repdf = df.loc[get_legis(113, 'rep'), get_legis(113, 'rep')]

# make the adjacency matrix binary
brepdf = repdf
brepdf[brepdf > 0] = 1

# assign the labels using spectral clustering
labels = cluster.spectral_clustering(brepdf.as_matrix(), n_clusters=2)

# create the graph layout
pos = networkx.random_layout(graph)

# this function is heavily borrowed from
# http://stackoverflow.com/questions/17381006/large-graph-visualization-with-python-and-networkx
# although I did modify it quite a bit
def save_graph(graph,file_name,ps,col,wd):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    networkx.draw_networkx_nodes(graph,ps,node_size=100,node_color=col)
    networkx.draw_networkx_edges(graph,ps, alpha=0.5, width=wd)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in ps.values())+.1
    ymax = cut * max(yy for xx, yy in ps.values())+.1
    print(ymax)
    plt.xlim(-.1, xmax)
    plt.ylim(-.1, ymax)

    plt.savefig(file_name,bbox_inches="tight")
    pylab.close()
    del fig

# this is how I created the plots I have left it commented out so it doesn't run
#graph = networkx.from_numpy_matrix(brepdf.as_matrix())
#pos = networkx.random_layout(graph)
# this is the visualization of the network with the color according to the
# labels assigned by spectral clustering algorithm
#save_graph(graph, '113graphclus2.png',pos,clus2colors, 0.03125)
# this is the visualization of the network with the color according to the
# actual party of the congressperson
#save_graph(graph, '113graphparty.png',pos,colorparties, 0.03125)

# have I take a tally of how many were correctly predicted.
tr = 0

for i in range(len(parties)):
    if partypred[i] == parties[i]:
        tr += 1
