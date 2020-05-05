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
        if setup:
            self.__setup_database(config)

    def __setup_database(self, config):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE orders (order_id uuid CONSTRAINT orders_pk PRIMARY KEY, user_id uuid NOT NULL);
        CREATE INDEX orders_user_id_index ON orders (user_id);
        ''')

        cursor.execute('''
        CREATE TABLE order_items (
        order_id uuid, item_id uuid, amount int, CONSTRAINT order_items_pk PRIMARY KEY (order_id, item_id)
        );
        ''')
        self.connection.commit()
        cursor.close()

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
