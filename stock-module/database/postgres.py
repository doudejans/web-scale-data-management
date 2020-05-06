import uuid

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
        self.connection.autocommit = True
        psycopg2.extras.register_uuid()
        if setup:
            self.__setup_database(config)

    def __setup_database(self, config):
        cur = self.connection.cursor()
        cur.execute(f'''
                    CREATE TABLE IF NOT EXISTS stock (
                        item_id uuid,
                        amount integer
                    );
                ''')
        pass

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

    def get_availability(self, item_id):
        cur = self.connection.cursor()
        cur.execute(f'''
               SELECT amount FROM stock
               WHERE item_id = %s;
               ''', (item_id,))
        res = cur.fetchone()
        return None if res is None else res[0]

    def stock_subtract(self, item_id, number):
        cur = self.connection.cursor()
        cur.execute(f'''
                           UPDATE stock
                           SET amount = amount - %s
                           WHERE item_id = %s
                           AND amount >= %s;
                       ''', (number, item_id, number))
        return cur.rowcount == 1

    def stock_add(self, item_id, number):
        cur = self.connection.cursor()
        cur.execute(f'''
                    UPDATE stock
                    SET amount = amount + %s
                    WHERE item_id = %s;
                ''', (number, item_id))
        return cur.rowcount == 1

    def create_stock(self):
        item_id = uuid.uuid4()
        cur = self.connection.cursor()
        cur.execute(f'''
            INSERT INTO stock (item_id, amount)
            VALUES (%s, 0);
        ''', (item_id,))
        self.connection.commit()
        return item_id
