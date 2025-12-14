Query | DB      | 10k nodes / 30k edges | 30k nodes / 150k edges | 1M nodes / 3M edges
---------------------------------------------------------------------------------------
Q1    | SQL     | 7.15 s                | 105 s                  | 5 h (est.)
Q1    | Neo4j   | 12 ms                 | 32 ms                  | 640 ms
Q1    | Arango  | 232 ms                | 673 ms                 | 25.9 s

Q2    | SQL     | 67.5 s                | 1877 s                 | >10 d (est.)
Q2    | Neo4j   | 76 ms                 | 177 ms                 | 350 ms
Q2    | Arango  | 469 ms                | 1.1 s                  | 56 s

Q3    | SQL     | 0 ms                  | 4 ms                   | 6.0 s
Q3    | Neo4j   | 177 ms                | 96 ms                  | 190 ms
Q3    | Arango  | 319 ms                | 1.2 s                  | 45 s

Q4    | SQL     | 0 ms                  | 0 ms                   | 3 ms
Q4    | Neo4j   | 14 ms                 | 19 ms                  | 380 ms
Q4    | Arango  | 1.4 ms                | 3.5 ms                 | 100 ms

Q5    | SQL     | 120 ms                | 250 ms                 | 286 h (est.)
Q5    | Neo4j   | 120 ms                | 600 ms                 | 12 s
Q5    | Arango  | 354 ms                | 1.37 s                 | 58 s

Q6    | SQL     | 15 ms                 | 40 ms                  | 60 s
Q6    | Neo4j   | 37 ms                 | 77 ms                  | 150 ms
Q6    | Arango  | 7.6 ms                | 9.5 ms                 | 314 ms


DB     | Data type | 10k nodes / 30k edges | 30k nodes / 150k edges | 1M nodes / 3M edges
------------------------------------------------------------------------------------------
SQL    | Nodes     | 0.43 s                | 0.25 s                | 1 s
SQL    | Edges     | 0.55 s                | 1.16 s                | 5 s

Arango | Nodes     | 0.12 s                | 0.28 s                | 1.64 s
Arango | Edges     | 0.55 s                | 1.44 s                | 12.75 s