
import matplotlib.pyplot as plt
import numpy as np

sizes = np.array([30_000, 150_000, 3_000_000])


def to_seconds(values):
    out = []
    for v in values:
        if isinstance(v, str):
            v = v.strip()
            if "h" in v:
                out.append(float(v.replace("h","")) * 3600)
            elif "d" in v:
                out.append(float(v.replace("d","")) * 86400)
            elif "ms" in v:
                out.append(float(v.replace("ms","")) / 1000)
            elif "s" in v:
                out.append(float(v.replace("s","")))
            else:
                out.append(np.nan)
        else:
            out.append(v)
    return np.array(out, dtype=float)

queries = {
    "Q1": {
        "SQL": to_seconds(["7.15 s", "105 s", "5 h"]),
        "Neo4j": to_seconds(["12 ms", "32 ms", "640 ms"]),
        "Arango": to_seconds(["232 ms", "673 ms", "25.9 s"]),
    },
    "Q2": {
        "SQL": to_seconds(["67.5 s", "1877 s", "10 d"]),
        "Neo4j": to_seconds(["76 ms", "177 ms", "350 ms"]),
        "Arango": to_seconds(["469 ms", "1.1 s", "56 s"]),
    },
    "Q3": {
        "SQL": to_seconds(["0 ms", "4 ms", "6.0 s"]),
        "Neo4j": to_seconds(["177 ms", "96 ms", "190 ms"]),
        "Arango": to_seconds(["319 ms", "1.2 s", "45 s"]),
    },
    "Q4": {
        "SQL": to_seconds(["0 ms", "0 ms", "3 ms"]),
        "Neo4j": to_seconds(["14 ms", "19 ms", "380 ms"]),
        "Arango": to_seconds(["1.4 ms", "3.5 ms", "100 ms"]),
    },
    "Q5": {
        "SQL": to_seconds(["120 ms", "250 ms", "286 h"]),
        "Neo4j": to_seconds(["120 ms", "600 ms", "12 s"]),
        "Arango": to_seconds(["354 ms", "1.37 s", "58 s"]),
    },
    "Q6": {
        "SQL": to_seconds(["15 ms", "40 ms", "60 s"]),
        "Neo4j": to_seconds(["37 ms", "77 ms", "150 ms"]),
        "Arango": to_seconds(["7.6 ms", "9.5 ms", "314 ms"]),
    },
}

for q, data in queries.items():
    plt.figure()
    for db, vals in data.items():
        plt.plot(sizes, vals, marker='o', label=db)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Number of nodes (log scale)")
    plt.ylabel("Runtime (seconds, log scale)")
    plt.title(f"{q} runtime vs dataset size")
    plt.legend()
    plt.tight_layout()
    plt.show()

insert_nodes = {
    "SQL": to_seconds(["0.43 s", "0.25 s", "1 s"]),
    "Arango": to_seconds(["0.12 s", "0.28 s", "1.64 s"]),
    "Neo4j": to_seconds(["305 ms", "255 ms", "14422 ms"]),
}
insert_edges = {
    "SQL": to_seconds(["0.55 s", "1.16 s", "5 s"]),
    "Arango": to_seconds(["0.55 s", "1.44 s", "12.75 s"]),
    "Neo4j": to_seconds(["493 ms", "1296 ms", "51562 ms"]),
}


plt.figure()
for db, vals in insert_nodes.items():
    plt.plot(sizes, vals, marker='o', label=db)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Number of nodes (log scale)")
plt.ylabel("Insertion time (seconds, log scale)")
plt.title("Node insertion time vs dataset size")
plt.legend()
plt.tight_layout()
plt.show()

plt.figure()
for db, vals in insert_edges.items():
    plt.plot(sizes, vals, marker='o', label=db)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Number of edges (log scale)")
plt.ylabel("Insertion time (seconds, log scale)")
plt.title("Edge insertion time vs dataset size")
plt.legend()
plt.tight_layout()
plt.show()
