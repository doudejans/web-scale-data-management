import psycopg2
import psycopg2.extras
from database.database import Database, DatabaseException

psycopg2.extras.register_uuid()


# This file connects to the postgres database, it should expose the same
# functions as the other database models (db_cassandra.py).

class PostgresDB(Database):
    DATABASE = "POSTGRES"
    connection = None

    def connect(self, config, setup):
        connection_config = config['connection']
        self.connection = psycopg2.connect(host=connection_config["host"],
                                           user=connection_config["user"],
                                           database=connection_config[
                                               "database"],
                                           password=connection_config[
                                               "password"])
        # TODO: Add specific connection code, if needed.
        self.connection.autocommit = True
        if setup:
            self.__setup_database(config)

    def __get_cursor(self):
        """Retrieve a new cursor for the connection."""
        return self.connection.cursor()

    def __setup_database(self, config):
        cur = self.__get_cursor()
        cur.execute(f"""
        CREATE TYPE payment_status AS ENUM ('PAID', 'CANCELLED');
        CREATE TABLE IF NOT EXISTS order_payment_status (
            order_id uuid,
            status payment_status,
            amount integer
        );
        """)

    def insert_payment_status(self, order_id, status, amount):
        try:
            with self.__get_cursor() as cur:
                cur.execute("""
                INSERT INTO order_payment_status (order_id, status, amount)
                VALUES (%s, %s, %s);
                """, (order_id, status, amount))
        except Exception as e:
            raise DatabaseException(e)

    def set_payment_status(self, order_id, status):
        """Set the payment status for a specific order.
        """
        try:
            with self.__get_cursor() as cur:
                cur.execute("""
                UPDATE order_payment_status
                SET status = %s
                WHERE order_id = %s""",
                            (status, order_id))
        except Exception as e:
            raise DatabaseException(e)

    def get_payment(self, order_id):
        """Retrieve the status of a specific order.

        If no order matching the order_id could be found None is returned.
        """
        try:
            with self.__get_cursor() as cur:
                cur.execute("""
                SELECT status, amount FROM order_payment_status
                WHERE order_id = %s
                """, (order_id,))
                if cur.rowcount == 0:
                    return None, None
                # The row contains one item at idx 0 which is the status.
                result = cur.fetchone()
                return result[0], result[1]
        except Exception as e:
            raise DatabaseException(e)
