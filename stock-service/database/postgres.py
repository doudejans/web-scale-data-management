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
        psycopg2.extras.register_uuid()
        if setup:
            self.__setup_database(config)

    def __setup_database(self, config):
        cur = self.connection.cursor()
        cur.execute(f'''
                    CREATE TABLE IF NOT EXISTS stock (
                        item_id uuid,
                        amount integer,
                        price integer
                    );
                ''')
        self.connection.commit()
        pass

    def find_stock(self, item_id):
        cur = self.connection.cursor()
        cur.execute(f'''
               SELECT amount, price FROM stock
               WHERE item_id = %s;
               ''', (item_id,))
        res = cur.fetchone()
        return None if res is None else res[0], res[1]

    def stock_subtract(self, item_id, number):
        cur = self.connection.cursor()
        cur.execute(f'''
                           UPDATE stock
                           SET amount = amount - %s
                           WHERE item_id = %s
                           AND amount >= %s;
                       ''', (number, item_id, number))
        self.connection.commit()
        return cur.rowcount == 1

    def stock_add(self, item_id, number):
        cur = self.connection.cursor()
        cur.execute(f'''
                    UPDATE stock
                    SET amount = amount + %s
                    WHERE item_id = %s;
                ''', (number, item_id))
        self.connection.commit()
        return cur.rowcount == 1

    def create_stock(self, price):
        item_id = uuid.uuid4()
        cur = self.connection.cursor()
        cur.execute(f'''
            INSERT INTO stock (item_id, amount, price)
            VALUES (%s, 0, %s);
        ''', (item_id, price))
        self.connection.commit()
        return str(item_id)

    def batch_subtract(self, items):
        try:
            cur = self.connection.cursor()
            for item_id in items:
                cur.execute(f'''
                    UPDATE stock
                    SET amount = amount - %s
                    WHERE item_id = %s;
                ''', (1, item_id))
            self.connection.commit()
            return True
        except Exception:
            return False

