

LOAD CSV WITH HEADERS FROM 'file:///covid_dataset.csv' AS row
   CREATE (:Person {
       id: toInteger(row.id),
       first_name: row.first_name,
       last_name: row.last_name,
       age: toInteger(row.age),
       has_covid: row.has_covid = 'True'
});

LOAD CSV WITH HEADERS FROM 'file:///covid_relationships.csv' AS row
   MATCH (p1:Person {id: toInteger(row.from_id)})
   MATCH (p2:Person {id: toInteger(row.to_id)})
   CREATE (p1)-[:EXPOSED_TO {exposure: row.exposure}]->(p2);

