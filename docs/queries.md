# Queries

## Neo4j Covid19 Queries

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
       has_covid: row.has_covid = 'True',
       origin: row.origin
   });
   ```

2. **Load the relationships (edges):**

   ```cypher
   LOAD CSV WITH HEADERS FROM 'file:///covid_relationships.csv' AS row
   MATCH (p1:Person {id: toInteger(row.from_id)})
   MATCH (p2:Person {id: toInteger(row.to_id)})
   CREATE (p1)-[:EXPOSED_TO {
    exposure: row.exposure,
    from_origin: row.from_origin,
    to_origin: row.to_origin
   }]->(p2);
   ```

---

### 1. Count people who have at least one contact with covid

This query returns the **number of people** who are _directly connected_ to someone who has covid.

```cypher
MATCH (p:Person)-[:EXPOSED_TO]-(contact:Person {has_covid: true})
RETURN count(DISTINCT p);
```

### 2. Count people with no covid cases in their 2-degree circle

This query returns the **number of people** who do not have any _covid-positive contacts_ within `1` or `2` hops.

```cypher
MATCH (p:Person)
WHERE NOT EXISTS {MATCH (p)-[:EXPOSED_TO*1..2]-(contact:Person {has_covid: true})}
RETURN count(p);
```

### 3. Count healthy people at risk from CLOSE contacts

This query returns the number of **healthy people** `(has_covid = false)` who are in direct `CLOSE` contact with someone who has covid.

```cypher
MATCH (healthy:Person {has_covid: false})-[:EXPOSED_TO {exposure: 'CLOSE'}]-(infected:Person {has_covid: true})
RETURN count(DISTINCT healthy);
```

### 4. Count covided people of age 65+

This query returns the number of **covided people** `(has_covid = true)` who is older the 65. (This query is designed to be easy no matter the db type)

```cypher
MATCH (covided:Person {has_covid: true})
WHERE covided.age > 65
RETURN count(DISTINCT covided)
```

### 5. Contaminate people in relationships with covid cases:

```cypher
MATCH (healthy:Person {has_covid: false})
      -[:EXPOSED_TO {exposure: 'CLOSE'}]-
      (:Person {has_covid: true})

WITH DISTINCT healthy
ORDER BY rand()
WITH collect(healthy) AS close_people, $p AS p
WITH close_people, toInteger(size(close_people) * p) AS take_p
UNWIND close_people[0..take_p] AS new_cases
SET new_cases.has_covid = true
RETURN count(new_cases) AS newly_infected;
```

```cypher
MATCH (healthy:Person {has_covid: false})- [rel:EXPOSED_TO] - (infected:Person {has_covid: true})
WHERE rel.exposure = 'CASUAL'
WITH collect(DISTINCT healthy) AS casual_people, $q AS q
WITH casual_people, q, toInteger(size(casual_people) * q) AS take_q
UNWIND apoc.coll.randomSubset(casual_people, take_q) AS new_cases
SET new_cases.has_covid = true;
RETURN count(new_cases) AS newly_infected;
```

```cypher
MATCH (healthy:Person {has_covid: false})- [rel:EXPOSED_TO] - (infected:Person {has_covid: true})
WHERE rel.exposure = 'DISTANT'
WITH collect(DISTINCT healthy) AS distant_people, $r AS r
WITH distant_people, r, toInteger(size(distant_people) * r) AS take_r
UNWIND apoc.coll.randomSubset(distant_people, take_r) AS new_cases
SET new_cases.has_covid = true;
RETURN count(new_cases) AS newly_infected;
```

### 6. Kill people with covid

```cypher
MATCH (p:Person {has_covid: true})
WITH p,
     CASE 
        WHEN p.age >= 65 THEN $x
        WHEN p.age <= 5 THEN $x
        ELSE $y
     END AS death_rate
ORDER BY rand()
WITH collect({person: p, rate: death_rate}) AS people

WITH [p IN people WHERE rand() < p.rate | p.person] AS to_die,
     [p IN people WHERE rand() >= p.rate | p.person] AS to_survive

FOREACH (dead IN to_die | DETACH DELETE dead)

RETURN size(to_die) AS deaths;
```

# Arango Covid19 Queries

---

## Loading the datasets

With the "arangdb" already created (aside from the native "_system" db)

```bash
arangoimport --server.database "arangodb" --file import/covid_dataset.csv --type csv --collection persons --create-collection true
```

```bash
arangoimport --server.database "arangodb" --file /import/covid_relationships_edges.csv --type csv --collection exposed_to --create-collection true --create-collection-type edge
```

---

## 1. Count people who have at least one contact with covid

This query returns the **number of people** who are _directly connected_ to someone who has covid.

```AQL
FOR p IN persons
  LET hasExposure = (
    FOR contact IN ANY p exposed_to
      FILTER contact.has_covid == true
      LIMIT 1  // Stop when one was found
      RETURN 1
  )
  FILTER LENGTH(hasExposure) > 0
  COLLECT WITH COUNT INTO total // Count the number of element that would be returned
  RETURN total
```

### 2. Count people with no covid cases in their 2-degree circle

This query returns the **number of people** who do not have any _covid-positive contacts_ within `1` or `2` hops.

```AQL
FOR p IN persons
    LET hasCovidContact = (
        FOR contact IN 1..2 ANY p exposed_to
        FILTER contact.has_covid == true
        LIMIT 1
        RETURN 1
    )
    FILTER LENGTH(hasCovidContact) == 0
    COLLECT WITH COUNT INTO total
    RETURN total
```

### 3. Count healthy people at risk from CLOSE contacts

This query returns the number of **healthy people** `(has_covid = false)` who are in direct `CLOSE` contact with someone who has covid.

```AQL
FOR p IN persons
    FILTER p.has_covid == false
    LET closeCovid = (
        FOR contact, edge IN ANY p exposed_to
        FILTER edge.exposure == 'CLOSE' AND contact.has_covid
        LIMIT 1
        RETURN 1
    )
    FILTER LENGTH(closeCovid) > 0
    COLLECT WITH COUNT INTO total
    RETURN total
```

### 4. Count covided people of age 65+

This query returns the number of **covided people** `(has_covid = true)` who is older the 65. (This query is designed to be easy no matter the db type)

```AQL
FOR p IN persons
    FILTER p.has_covid && p.age > 65
    COLLECT WITH COUNT INTO total
    RETURN total
```

### 5. Contaminate people in relationships with covid cases:

```AQL
LET exposed_people = (
  FOR healthy IN persons
    FILTER healthy.has_covid == false
    FOR v, e IN 1..1 ANY healthy exposed_to
      FILTER v.has_covid == true
      FILTER e.exposure == @exposure_type
      RETURN DISTINCT healthy
)

LET sample_size = FLOOR(LENGTH(exposed_people) * @transmission_rate)

LET shuffled = (
  FOR person IN exposed_people
    SORT RAND()
    RETURN person
)

LET selected = SLICE(shuffled, 0, sample_size)

LET new_cases = (
  FOR person IN selected
    UPDATE person WITH { has_covid: true } IN persons
    RETURN NEW
)

RETURN { newly_infected: LENGTH(new_cases) }
```

### 6. Kill people with covid

```AQL
LET results = (
  FOR person IN persons
    FILTER person.has_covid == true
    LET death_rate = (person.age >= 65 || person.age <= 5) ? @x : @y
    LET dies = RAND() < death_rate
    FILTER dies == true
    REMOVE person IN persons
    RETURN OLD
)

RETURN { deaths: LENGTH(results) }
```

# SQLite Covid19 Queries

---

## 1. Count people who have at least one contact with covid

This query returns the number of people who were in _direct_ contact with at least one person who had covid.

```sql
SELECT COUNT(*) as count
FROM Person p
WHERE EXISTS (
    SELECT 1
    FROM EXPOSED_TO e
    WHERE (e.from_id = p.id
                AND EXISTS (SELECT 1 FROM Person c WHERE c.id = e.to_id AND c.has_covid = TRUE)
        OR (e.to_id = p.id
                AND EXISTS (SELECT 1 FROM Person c WHERE c.id = e.from_id AND c.has_covid = TRUE)
        )
    )
);
```

## 2. Count people with no covid cases in their 2-degree circle

This query returns the **number of people** who do not have any _covid-positive contacts_ within `1` or `2` hops.

```sql
WITH direct AS (
    SELECT DISTINCT p.id as person_id
    FROM Person p
    JOIN EXPOSED_TO e
        ON p.id = e.from_id OR p.id = e.to_id
    JOIN Person inf
        ON (inf.id = e.from_id AND p.id = e.to_id) OR
            (inf.id = e.to_id AND p.id = e.from_id)
    WHERE inf.has_covid = TRUE
),
two_hop AS (
    SELECT DISTINCT p.id AS person_id
    FROM Person p
    JOIN EXPOSED_TO e1
        ON p.id = e1.from_id OR p.id = e1.to_id
    JOIN Person mid
        ON mid.id = CASE
                        WHEN p.id = e1.from_id THEN e1.to_id
                        ELSE e1.from_id
                    END
    JOIN EXPOSED_TO e2
        ON mid.id = e2.from_id OR mid.id = e2.to_id
    JOIN Person inf
        ON inf.id = CASE
                        WHEN mid.id = e2.from_id THEN e2.to_id
                        ELSE e2.from_id
                    END
    WHERE inf.has_covid = TRUE
);

SELECT COUNT(*) AS count
    FROM Person p
WHERE p.id NOT IN (
    SELECT person_id FROM direct
    UNION
    SELECT person_id FROM two_hop
);
```

## 3. Count healthy people at risk from CLOSE contacts

People with `has_covid = FALSE` who are in direct contact (edge exposure = "CLOSE") with someone who has covid.

```sql
SELECT COUNT(DISTINCT p.id) AS count
FROM Person p
JOIN EXPOSED_TO e
    ON p.id = e.from_id OR p.id = e.to_id
JOIN Person inf
    ON inf.id = CASE
                    WHEN p.id = e.from_id THEN e.to_id
                    ELSE e.from_id
                END
WHERE p.has_covid = FALSE
  AND inf.has_covid = TRUE
  AND e.exposure = 'CLOSE';
```

## 4. Count covided people of age 65+

```sql
SELECT COUNT(*) AS count
FROM Person
WHERE has_covid = TRUE
  AND age > 65;
```

## 5. Contaminate people in relationships with covid cases:

```sql
WITH healthy_exposed AS (
    SELECT DISTINCT p1.id
    FROM Person p1
    JOIN EXPOSED_TO e
      ON (p1.id = e.from_id OR p1.id = e.to_id)
    JOIN Person p2
      ON (p2.id = e.from_id OR p2.id = e.to_id)
    WHERE p1.has_covid = FALSE
      AND p2.has_covid = TRUE
      AND e.exposure = 'CLOSE'
      AND p1.id <> p2.id
),
picked AS (
    SELECT id
    FROM healthy_exposed
    ORDER BY RANDOM()
    LIMIT (
        SELECT CAST(COUNT(*) * :p AS INTEGER)
        FROM healthy_exposed
    )
)
UPDATE Person
SET has_covid = TRUE
WHERE id IN (SELECT id FROM picked)
RETURNING COUNT(*) AS newly_infected;
```

## 6. Kill people with covid

```sql
WITH infected AS (
    SELECT
        id,
        CASE
            WHEN age >= 65 THEN :x
            WHEN age <= 5  THEN :x
            ELSE :y
        END AS death_rate
    FROM Person
    WHERE has_covid = TRUE
),
marked AS (
    SELECT
        id,
        death_rate,
        RANDOM() AS r
    FROM infected
),
to_die AS (
    SELECT id
    FROM marked
    WHERE r < death_rate
)
DELETE FROM Person
WHERE id IN (SELECT id FROM to_die)
RETURNING COUNT(*) AS deaths;
```
