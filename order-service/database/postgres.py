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
            order = cursor.fetchone()

            if order:
                cursor.execute('''
                SELECT item_id, amount FROM order_items WHERE order_id = %s
                ''', (order_id, ))

                items = cursor.fetchall()

                return {
                    'order_id': order_id,
                    'user_id': order[0],
                    'items': [{'item_id': item[0], 'amount': item[1]} for item in items]
                }
            else:
                return None

    def add_item_to_order(self, order_id, item_id):
        psycopg2.extras.register_uuid()
        with self.connection.cursor() as cursor:
            cursor.execute('''
            SELECT * FROM orders WHERE order_id = %s;
            ''', (order_id, ))

            if cursor.fetchone() is None:
                return False

            cursor.execute('''
            INSERT INTO order_items (order_id, item_id, amount) VALUES (%s, %s, 1)
            ON CONFLICT (order_id, item_id) DO UPDATE SET amount = order_items.amount + 1;
            ''', (order_id, item_id))
            self.connection.commit()

            return True

    def remove_item_from_order(self, order_id, item_id):
        psycopg2.extras.register_uuid()
        with self.connection.cursor() as cursor:
            cursor.execute('''
            SELECT * FROM orders WHERE order_id = %s;
            ''', (order_id, ))

            if cursor.fetchone() is None:
                return False

            cursor.execute('''
            UPDATE order_items SET amount = amount - 1 WHERE order_id = %s AND item_id = %s;
            ''', (order_id, item_id))
            cursor.execute('''
            DELETE FROM order_items WHERE order_id = %s AND item_id = %s AND amount = 0;
            ''', (order_id, item_id))

            self.connection.commit()
            return True

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
