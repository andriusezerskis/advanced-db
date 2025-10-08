
from neo4j import GraphDatabase
from enum import Enum
from typing import Optional, List



class TemplateRequests(Enum):

    """Enum for Cypher query templates. Please ensure to use parameterized queries when necessary."""

    ADD_USER: str = """CREATE (p:Person {id: $id, first_name: $first_name, last_name: $last_name, age: $age, has_covid: $has_covid});"""
    GET_ALL_USERS: str = """MATCH (p:Person) RETURN p;"""
    GET_USER: str = """MATCH (p:Person {id: $id}) RETURN p.id AS id, p.first_name AS first_name, p.last_name AS last_name, p.age AS age, p.has_covid AS has_covid;"""

    def list_params(self) -> List[str]:
        """List all parameters used in the query template."""
        return [part[1:] for part in self.value.split() if part.startswith("$")]


class Neo4JDB:

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD) -> None:

        """Initialize the Neo4JDB instance."""
        
        self.driver: GraphDatabase = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        self.driver.close()

    def run_cypher(self, query: str, parameters: Optional[dict] = None) -> List:

        """
        Execute a Cypher query and return the results as a list.
        This might raise an exception if the query is invalid or if there are connection issues.
        """
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    def run_schema_cypher(self, fp: str) -> None:
        
        """
        Execute a Cypher query from a file to set up the database schema.
        This might raise an exception if the file is not found or if the query is invalid.
        """
        
        with open(fp, 'r', encoding='utf-8') as file:
            
            statements: str = [stmt.strip() for stmt in file.read().split(";") if stmt.strip()]

            for stmt in statements:
                self.run_cypher(stmt)
    


if __name__ == "__main__":

    ...

    # Example usage:

    # db = Neo4JDB()
    # db.run_schema_cypher(r"dockers/neo4j-docker/import/schema.cypher")
    # db.run_schema_cypher(r"dockers/neo4j-docker/import/fill_dataset.cypher")
    # db.close()
