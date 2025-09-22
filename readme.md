## Running Neo4j with Docker Compose

To spin up a Neo4j instance using Docker Compose, follow these steps:

1. Open a terminal and navigate to the directory containing the `docker-compose.yml` file.

2. Run the following command to start the Neo4j container:

   ```bash
   docker-compose up -d
   ```

3. Access the Neo4j Browser at [http://localhost:7474](http://localhost:7474) and log in with the credentials `neo4j` and `password`.

4. To stop the container, use:
   ```bash
   docker-compose down
   ```

Ensure Docker is installed and running on your system before executing these steps.
