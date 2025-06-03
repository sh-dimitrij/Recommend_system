import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("B", "D")])

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightgreen', font_size=12, arrows=True)
plt.show()