# Neo4j Covid19 Queries

This document contains some **Cypher queries** to analyze stuff in our `covid19` contact graph.

Before running the queries, make sure you **load the datasets** into your neo4j instance:

---

## Loading the datasets

1. **Load the nodes (people):**

    ```cypher
    LOAD CSV WITH HEADERS FROM 'file:///covid_dataset.csv' AS row
    CREATE (:Person {
        id: toInteger(row.id),
        first_name: row.first_name,
        last_name: row.last_name,
        age: toInteger(row.age),
        has_covid: row.has_covid = 'True'
    });
    ```

2. **Load the relationships (edges):**

    ```cypher
    LOAD CSV WITH HEADERS FROM 'file:///covid_relationships.csv' AS row
    MATCH (p1:Person {id: toInteger(row.from_id)})
    MATCH (p2:Person {id: toInteger(row.to_id)})
    CREATE (p1)-[:EXPOSED_TO {exposure: row.exposure}]->(p2);
    ```

---

### 1. Count people who have at least one contact with covid

This query returns the **number of people** who are *directly connected* to someone who has covid.

```cypher
MATCH (p:Person)-[:EXPOSED_TO]-(contact:Person {has_covid: true})
RETURN count(DISTINCT p);
```

### 2. Count people with no covid cases in their 2-degree circle

This query returns the **number of people** who do not have any *covid-positive contacts* within `1` or `2` hops.

```cypher
MATCH (p:Person)
WHERE NOT EXISTS {MATCH (p)-[:EXPOSED_TO*1..2]-(contact:Person {has_covid: true})}
RETURN count(p);
```

### 3. Count healthy people at risk from CLOSE contacts

This query returns the number of **healthy people** `(has_covid = false)` who are in direct `CLOSE` contact with someone who has covid.

```cypher
MATCH (healthy:Person {has_covid: false})-[:EXPOSED_TO {exposure: 'CLOSE'}]->(infected:Person {has_covid: true})
RETURN count(DISTINCT healthy);
```
