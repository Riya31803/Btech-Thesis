import pandas as pd
import networkx as nx
from community import community_louvain

file_path = "2011_aggregated - Agri-Food & Beverages.csv"  # Update with actual file path
df = pd.read_csv(file_path)

G = nx.Graph()

for _, row in df.iterrows():
    G.add_edge(row["Reporter Country"], row["Partner Country"], weight=row["Trade Value"])

# Louvain method
partition = community_louvain.best_partition(G, weight='weight')
modularity = community_louvain.modularity(partition, G, weight='weight')

print(f"Modularity of the trade network: {modularity}")
