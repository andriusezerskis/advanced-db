
import sqlite3
from typing import List, Dict, Any, Union
import csv
from datetime import datetime


# Alias
record_t = Dict[str, Any]


class SQLiteCovidDB:

    """
    Helper class to create a SQLite3 database for Covid-19 datasets.
    Nodes are represented as a `Person` table and relationships as an `EXPOSED_TO` table.
    """

    _PERSON_TABLE: str = """
            CREATE TABLE IF NOT EXISTS Person (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                has_covid BOOLEAN NOT NULL
            )
        """
    _RELATIONSHIP_TABLE: str = """
            CREATE TABLE IF NOT EXISTS EXPOSED_TO (
                id INTEGER PRIMARY KEY,
                from_id INTEGER NOT NULL,
                to_id INTEGER NOT NULL,
                exposure TEXT NOT NULL,
                FOREIGN KEY (from_id) REFERENCES Person(id),
                FOREIGN KEY (to_id) REFERENCES Person(id)
            )
        """
    _SEPARATOR: str = "=" * 40

    def __init__(self, dbfp: str) -> None:

        """Initialize the database connection."""

        self.dbfp: str = dbfp
        self.conn: sqlite3.Connection = sqlite3.connect(dbfp)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

        # Create tables if they do not exist
        self._setup()

    def _setup(self) -> None:

        # This is the setup method. This will create the tables if they do not exist.
        # Structure is exactly like the neo4j version.
        # This is NOT made to be efficient, just used for the benchmarking.

        self.cursor.execute(self._PERSON_TABLE)
        self.cursor.execute(self._RELATIONSHIP_TABLE)
        self.conn.commit()

    def _read_csv(self, fp: str) -> List[record_t]:
        
        # Read CSV file and return list of dictionaries
        # We are going to raise a ValueError if the CSV is empty

        with open(fp, newline='', encoding='utf-8') as f:
            reader: csv.DictReader = csv.DictReader(f)
            rows: List[record_t] = list(reader)
        
        if not rows:
            raise ValueError(f"CSV file {fp} is empty or invalid.")

        return rows

    def _handle_value(self, val: Union[int, Any]) -> Union[int, Any]:

        # Helper to handle value conversion, mainly for booleans and integers

        if val.lower() in ('true', 'false'):
            val: int = int(val.lower() == 'true')  # smart python line uh? im a wizard :3
        elif val.isdigit():
            val: int = int(val)
        
        return val

    def import_csv(self, table: str, fp: str, verbose: bool = True) -> None:

        """
        Import data from a CSV file into the specified table.
        The CSV file must have a header row with column names matching the table schema. \n
        Raises `ValueError` if the CSV is empty or invalid.
        """
        
        rows: List[record_t] = self._read_csv(fp)
        columns: List[str] = list(rows[0].keys())
        placeholders: str = ','.join(['?'] * len(columns))
        query: str = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        data: List[tuple] = list()

        for row in rows:
            r: List[Any] = list()
            for col in columns:
                val: Any = row[col]
                r.append(self._handle_value(val))  # will convert to int if possible (for booleans and string integers)
            data.append(tuple(r))

        # benchmarking with datetime
        t1: datetime = datetime.now()
        for row in data:
            try:
                self.cursor.execute(query, row)  # insert row
            except sqlite3.IntegrityError as e:
                if verbose: print(f"Warning: Could not insert row {row}. Error: {e}")
        t2: datetime = datetime.now()

        if verbose:
            print(f"\n{self._SEPARATOR}\n>> Table: {table}\n>> Imported rows: {len(data)}\n>> Time taken: {t2 - t1}s\n{self._SEPARATOR}\n")
        
        self.conn.commit()  # commit all changes

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()


if __name__ == "__main__":
    
    fp: str = r'res/covid.db'
    db: SQLiteCovidDB = SQLiteCovidDB(fp)

    # Uncomment the lines below to import data from CSV files (correct paths needed)

    # db.import_csv('Person', r'res/covid_dataset.csv')
    # db.import_csv('EXPOSED_TO', r'res/covid_relationships.csv')

    db.close()

