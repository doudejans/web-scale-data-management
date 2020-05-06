import psycopg2
import psycopg2.extras
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

    def add_order(self, order_id, user_id):
        psycopg2.extras.register_uuid()
        with self.connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO orders (order_id, user_id) VALUES (%s, %s)
            ''', (order_id, user_id))
            self.connection.commit()

    def delete_order(self, order_id):
        psycopg2.extras.register_uuid()
        with self.connection.cursor() as cursor:
            cursor.execute('''
            DELETE FROM orders WHERE order_id = %s
            ''', (order_id, ))
            self.connection.commit()

    def get_order(self, order_id):
        psycopg2.extras.register_uuid()
        with self.connection.cursor() as cursor:
            cursor.execute('''
            SELECT user_id FROM orders WHERE order_id = %s
            ''', (order_id,))
            row = cursor.fetchone()

        return row[0] if row else None

    def __setup_database(self, config):
        with self.connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (order_id uuid CONSTRAINT orders_pk PRIMARY KEY, user_id uuid NOT NULL);
            CREATE INDEX IF NOT EXISTS orders_user_id_index ON orders (user_id);
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
            order_id uuid, item_id uuid, amount int, CONSTRAINT order_items_pk PRIMARY KEY (order_id, item_id)
            );
            ''')
            self.connection.commit()
