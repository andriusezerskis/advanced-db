MATCH (n) DETACH DELETE n;

CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person)
REQUIRE p.id IS UNIQUE;

CREATE INDEX person_first_name IF NOT EXISTS
FOR (p:Person)
ON (p.first_name);

CREATE INDEX person_last_name IF NOT EXISTS
FOR (p:Person)
ON (p.last_name);

CREATE INDEX person_age IF NOT EXISTS
FOR (p:Person)
ON (p.age);

CREATE INDEX person_has_covid IF NOT EXISTS
FOR (p:Person)
ON (p.has_covid);

CALL db.createRelationshipType("EXPOSED_TO");
