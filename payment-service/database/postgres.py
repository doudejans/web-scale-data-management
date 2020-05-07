import psycopg2
from database.database import Database


# This file connects to the postgres database, it should expose the same
# functions as the other database models (db_cassandra.py).

class PostgresDB(Database):
    DATABASE = "POSTGRES"
    connection = None

    def connect(self, config, setup):
        connection_config = config['connection']
        self.connection = psycopg2.connect(host=connection_config["host"],
                                           user=connection_config["user"],
                                           database=connection_config["database"],
                                           password=connection_config["password"])
        # TODO: Add specific connection code, if needed.
        if setup:
            self.__setup_database(config)

    def __setup_database(self, config):
        cur = self.connection.cursor()
        cur.execute(f"""
        CREATE TYPE payment_status AS ENUM ('PAID', 'CANCELLED');
        CREATE TABLE IF NOT EXISTS order_payment_status (
            order_id uuid,
            status payment_status
        );
        """)

    def retrieve_version(self):
        # This is an example for a query. The same query, with the same function
        # name, parameters and return type, should be implemented for the other
        # database.
        curr = self.connection.cursor()
        curr.execute("""
            SELECT version()
        """)
        result = curr.fetchone()
        return result
