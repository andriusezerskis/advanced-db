# Running Neo4j with Docker Compose

To spin up a Neo4j instance using Docker Compose, follow these steps:

1. Open a terminal and navigate to the directory containing the `docker-compose.yml` file.

2. Run the following command to start the Neo4j container:

   ```bash
   docker-compose up -d  # you might need to use sudo
   ```

3. Access the Neo4j Browser at [http://localhost:7474](http://localhost:7474) and log in with the credentials `neo4j` and `password`.

4. To stop the container, use:

   ```bash
   docker-compose down  # you might need to use sudo
   ```

5. To erease the content of the container, use:

   ```bash
   docker volume rm neo4j-docker_neo4j_data  # use docker volume ls to find the correct name
   ```

Ensure Docker is installed and running on your system before executing these steps.

# Running ArangoDB with Docker compose

Same as Neo4j, but the localhost link is [http://localhost:8529](http://localhost:8529). The username is `root`, and password is `password`.

```bash
arangosh --server.username root --server.password "password" --server.database "example"
  --javascript.execute-string 'if (db._collection("exposed_to")) db.exposed_to.drop(); if (db._collection("persons")) db.persons.drop(); db._create("persons"); db._createEdgeCollection("exposed_to");'
```

```bash
arangoimport --file import/covid_dataset.csv --type csv --collection persons --create-collection true
```

```bash
awk -F',' 'NR==1 {print "_key,_from,_to,exposure,from_origin,to_origin"; next} {printf "%s,persons/%s,persons/%s,%s,%s,%s\n", $1, $2, $3, $4, $5, $6}' /import/covid_relationships.csv > /import/covid_relationships_edges.csv
```

```bash
arangoimport --file /import/covid_relationships_edges.csv --type csv --collection exposed_to --create-collection false --server.username root --server.password password
```
