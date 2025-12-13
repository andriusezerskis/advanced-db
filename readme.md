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
arangosh --server.username root --server.password "password" --server.database "arangodb"
  --javascript.execute-string 'if (db._collection("exposed_to")) db.exposed_to.drop(); if (db._collection("persons")) db.persons.drop(); db._create("persons"); db._createEdgeCollection("exposed_to");'
```

Convert True/False to allow boolean recognition : 

```bash
sed '1!s/True/true/g; 1!s/False/false/g' /import/covid_dataset.csv > /import/covid_dataset_cleaned.csv
```

Load the nodes:

```bash
arangoimport --server.database "arangodb" --server.password "password" --file import/covid_dataset10k_.csv --type csv --collection persons --overwrite true --create-collection true --translate "id=_key" --convert true
```

Create the edges.csv with arango field names:

```bash
awk -F',' 'NR==1 {print "_key,_from,_to,exposure"; next} {printf "%s,persons/%s,persons/%s,%s\n", $1, $2, $3, $4}' /import/covid_relationships30k.csv > /import/covid_relationships30k_.csv
```

Load the relationships:

```bash
arangoimport --server.database "arangodb" --server.password "password" --file /import/covid_relationships30k_.csv --type csv --collection exposed_to --overwrite true --create-collection true --create-collection-type edge
```

Graph setup:

   - Via [http://localhost:8529](http://localhost:8529): create a GeneralGraph with "exposed_to" collection as edge and "persons" collection as both the from and to collections
   - Change the settings to update the view.

How to query:

   - Sign in db:
      ```bash
      arangosh --server.username root --server.password "password" --server.database "arangodb"
      ```

   - Switch db:
      ```javascript
      db._useDatabase("db");
      ```

   - Query:
      For limited results:
      ```javascript
      db._query("your query");
      ```  

      For exhaustive results:
      ```javascript
      db._query("your query").toArray(); 
      ```  
