import matplotlib.pyplot as plt
import numpy as np

datasets = ["10k / 30k", "30k / 150k", "1M / 3M"]
dbs = ["SQL", "Arango", "Neo4J"]

sizes_mb = {
    "SQL":    [0.964, 4.05, 101],
    "Arango": [7.68, 35.96, 685.33],
    "Neo4J":  [5.39, 12.4, 566],
}

colors = {
    "SQL": "#1f77b4",     # blue
    "Arango": "#2ca02c",  # orange
    "Neo4J": "#e79658",   # green
}

x = np.arange(len(datasets))
width = 0.25
depth = 0.04

plt.figure()

for i, db in enumerate(dbs):
    xpos = x + i * width

    plt.bar(
        xpos + depth,
        sizes_mb[db],
        width,
        color=colors[db],
        alpha=0.6
    )

    plt.bar(
        xpos,
        sizes_mb[db],
        width,
        color=colors[db],
        label=db
    )

plt.yscale("log")
plt.xticks(x + width, datasets)
plt.ylabel("Database size (MB, log scale)")
plt.xlabel("Dataset size")
plt.title("Database storage size vs dataset scale")
plt.legend()
plt.tight_layout()
plt.show()
