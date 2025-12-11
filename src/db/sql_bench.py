
import sqlite3
import csv
from typing import List, Tuple
import time


class SQLITEDB:

    query1: str = """
    SELECT COUNT(*) as count
    FROM Person p
    WHERE EXISTS (
        SELECT 1
        FROM EXPOSED_TO e
        WHERE (
                e.from_id = p.id
                AND EXISTS (SELECT 1 FROM Person c WHERE c.id = e.to_id AND c.has_covid = TRUE)
            )
            OR (
                e.to_id = p.id
                AND EXISTS (SELECT 1 FROM Person c WHERE c.id = e.from_id AND c.has_covid = TRUE)
            )
    );
    """

    query2: str = """
    WITH direct AS (
        SELECT DISTINCT p.id as person_id
        FROM Person p
        JOIN EXPOSED_TO e
            ON p.id = e.from_id OR p.id = e.to_id
        JOIN Person inf
            ON (inf.id = e.from_id AND p.id = e.to_id)
            OR (inf.id = e.to_id AND p.id = e.from_id)
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
    )

    SELECT COUNT(*) AS count
    FROM Person p
    WHERE p.id NOT IN (
        SELECT person_id FROM direct
        UNION
        SELECT person_id FROM two_hop
    );
    """

    query3: str = """
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
    """

    query4: str = """
    SELECT COUNT(*) AS count
    FROM Person
    WHERE has_covid = TRUE
    AND age > 65;
    """

    def __init__(self, fp: str) -> None:

        """Initialize the database connection."""

        self.conn = sqlite3.connect(fp)
        self.cur = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.initialize()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def initialize(self) -> None:

        """Create the tables in the database."""

        self.cur.executescript("""
        CREATE TABLE IF NOT EXISTS Person (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            has_covid INTEGER  -- 0/1 instead of BOOLEAN
        );

        CREATE TABLE IF NOT EXISTS EXPOSED_TO (
            id INTEGER PRIMARY KEY,
            from_id INTEGER,
            to_id INTEGER,
            exposure TEXT,
            FOREIGN KEY(from_id) REFERENCES Person(id),
            FOREIGN KEY(to_id) REFERENCES Person(id)
        );
        """)

        self.conn.commit()

    def execute_query(self, query: str):
        """Execute a given SQL query and return the results."""
        t1: float = time.time()
        self.cur.execute(query)
        t2: float = time.time()
        print(f"Query executed in {t2 - t1:.4f} seconds.")
        return self.cur.fetchall()

    def insert_people(self, fp: str) -> None:

        """Insert people from a CSV file into the Person table."""
        people: List[Tuple[int, str, int, int]] = []

        with open(fp, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                name = f"{row['first_name']} {row['last_name']}"
                age = int(row['age'])
                has_covid = 1 if row['has_covid'].strip().lower() in ("true", "1") else 0
                person_id = int(row['id'])
                people.append((person_id, name, age, has_covid))

        self.cur.executemany("INSERT INTO Person VALUES (?, ?, ?, ?)", people)
        self.conn.commit()
        print(f"Inserted {len(people)} people into the database.")

    def insert_exposures(self, fp: str) -> None:

        """Insert exposure relationships from a CSV file into the EXPOSED_TO table."""
        edges: List[Tuple[int, int, int, str]] = []

        with open(fp, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                edge_id = int(row['id'])
                from_id = int(row['from_id'])
                to_id = int(row['to_id'])
                exposure = row['exposure'].strip().upper()
                edges.append((edge_id, from_id, to_id, exposure))

        self.cur.executemany("INSERT INTO EXPOSED_TO VALUES (?, ?, ?, ?)", edges)
        self.conn.commit()
        print(f"Inserted {len(edges)} exposure relationships into the database.")

if __name__ == "__main__":

    db: SQLITEDB = SQLITEDB("test.db")
    db.insert_people("res/covid_dataset1000k.csv")
    db.insert_exposures("res/covid_relationships3000k.csv")
    
    r3 = db.execute_query(SQLITEDB.query3)
    r4 = db.execute_query(SQLITEDB.query4)
    r1 = db.execute_query(SQLITEDB.query1)
    r2 = db.execute_query(SQLITEDB.query2)
