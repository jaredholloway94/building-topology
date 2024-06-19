import json
import networkx as nx
from pyvis.network import Network
# from pprint import pprint

with open('rooms.json','r') as jsonfile:
    rooms = json.load(jsonfile)

with open('doors.json','r') as jsonfile:
    doors = json.load(jsonfile)

with open('stairs.json','r') as jsonfile:
    stairs = json.load(jsonfile)

# print('ROOMS\n')
# pprint(rooms)
# print('\n\n')

# print('DOORS\n')
# pprint(doors)
# print('\n\n')

# print('STAIRS\n')
# pprint(stairs)
# print('\n\n')

G = nx.MultiDiGraph()

G.add_nodes_from(rooms, color='red')
G.add_nodes_from(doors, color='blue')
G.add_nodes_from(stairs, color='green')

for u in rooms:
    for v in rooms[u]['doors']:
        G.add_edge(u,v)
    for v in rooms[u]['stairs']:
        G.add_edge(u,v)

for u in doors:
    for v in doors[u]['rooms']:
        G.add_edge(u,v)

for u in stairs:
    for v in stairs[u]['rooms']:
        G.add_edge(u,v)

net = Network(
    height='1500px',
    width='1500px',
    directed=True,
    notebook=False,
    neighborhood_highlight=True,
    select_menu=False,
    filter_menu=False
    )
net.from_nx(G)
net.show('BuildingTopologyGraph.html')

