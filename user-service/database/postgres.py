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
        with self.connection.cursor() as cur:
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                user_id uuid,
                credit integer
            );
            ''')
        pass

    def retrieve_version(self):
        # This is an example for a query. The same query, with the same function
        # name, parameters and return type, should be implemented for the other
        # database.
        with self.connection.cursor() as cur:
            cur.execute("""
                SELECT version()
            """)
            result = cur.fetchone()
            return result

    def create_user(self):
        user_id = uuid.uuid4()
        with self.connection.cursor() as cur:
            cur.execute('''
            INSERT INTO users (user_id, credit)
            VALUES (%s, 0);
            ''', (user_id,))
            return str(user_id)

    def remove_user(self, user_id):
        with self.connection.cursor() as cur:
            cur.execute('''
            DELETE FROM users
            WHERE user_id = %s;
            ''', (user_id,))
            return cur.rowcount == 1

    def get_credit(self, user_id):
        with self.connection.cursor() as cur:
            cur.execute('''
            SELECT credit FROM users
            WHERE user_id = %s;
            ''', (user_id,))
            res = cur.fetchone()
            return None if res is None else res[0]

    def credit_add(self, user_id, amount):
        with self.connection.cursor() as cur:
            cur.execute('''
            UPDATE users
            SET credit = credit + %s
            WHERE user_id = %s;
            ''', (amount, user_id))
            return cur.rowcount == 1

    def credit_subtract(self, user_id, amount):
        with self.connection.cursor() as cur:
            cur.execute('''
            UPDATE users
            SET credit = credit - %s
            WHERE user_id = %s
            AND credit >= %s;
            ''', (amount, user_id, amount))
            return cur.rowcount == 1
