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
        # TODO: Add specific connection code, if needed.
        if setup:
            self.__setup_database(connection_config)
        self.connection.set_keyspace(connection_config['keyspace'])

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
        CREATE TABLE IF NOT EXISTS order_items (order_id uuid, item_id uuid, amount int, PRIMARY KEY (order_id, item_id))
        ''')

    def retrieve_version(self):
        # This is an example for a query. The same query, with the same function
        # name, parameters and return type, should be implemented for the other
        # database.
        return self.connection.execute("""
          SELECT release_version FROM system.local
        """).one()
