from cassandra.cluster import Cluster, Session
from database.database import Database


# This file connects to the cassandra database, it should expose the same
# functions as the other database models (db_postgres.py).

class CassandraDB(Database):
    DATABASE = "CASSANDRA"
    connection: Session = None

    def connect(self, config, setup=False):
        cluster = Cluster()
        connection_config = config['connection']
        self.connection = cluster.connect()
        if setup:
            self.__setup_database(connection_config)
        self.connection.set_keyspace(connection_config['keyspace'])

    def add_order(self, order_id, user_id):
        self.connection.execute('''
        INSERT INTO orders (order_id, user_id) VALUES (%s, %s)
        ''', (order_id, user_id))

    def delete_order(self, order_id):
        self.connection.execute('''
        DELETE FROM orders WHERE order_id = %s
        ''', (order_id, ))

    def get_order(self, order_id):
        results = self.connection.execute('''
        SELECT user_id FROM orders WHERE order_id = %s
        ''', (order_id,))
        row = results.one()
        return row.user_id if row else None

    def add_item_to_order(self, order_id, item_id):
        results = self.connection.execute('''
        SELECT * FROM orders WHERE order_id = %s
        ''', (order_id,))

        if results.one() is None:
            return False

        self.connection.execute('''
        UPDATE order_items SET amount = amount + 1 WHERE order_id = %s AND item_id = %s
        ''', (order_id, item_id))

    def __setup_database(self, config):
        # Create the keyspace
        self.connection.execute(f'''
        CREATE KEYSPACE IF NOT EXISTS {config['keyspace']} with replication = {{
            'class':'SimpleStrategy','replication_factor':1
        }};
        ''')
        self.connection.set_keyspace(config['keyspace'])
        self.connection.execute('''
        CREATE TABLE IF NOT EXISTS orders (order_id uuid, user_id uuid, PRIMARY KEY (order_id, user_id))
        ''')

        self.connection.execute('''
        CREATE TABLE IF NOT EXISTS order_items (order_id uuid, item_id uuid, amount counter, PRIMARY KEY (order_id, item_id))
        ''')
