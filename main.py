

from src.db import Neo4JDB


if __name__ == "__main__":

    # initial setup

    db = Neo4JDB()
    db.run_schema_cypher(r"dockers/neo4j-docker/import/schema.cypher")
    db.close()
