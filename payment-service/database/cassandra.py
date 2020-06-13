from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, Session
from database.database import Database, DatabaseException


# This file connects to the cassandra database, it should expose the same
# functions as the other database models (db_postgres.py).

class CassandraDB(Database):
    DATABASE = "CASSANDRA"
    connection: Session = None

    def connect(self, config, setup=False):
        connection_config = config['connection']
        auth_provider = PlainTextAuthProvider(
            username=connection_config['user'],
            password=connection_config['password']) \
            if 'user' in connection_config else None
        cluster = Cluster([connection_config['host']], auth_provider=auth_provider)
        self.connection = cluster.connect()
        # TODO: Add specific connection code, if needed.
        if setup:
            self.__setup_database(connection_config)
        self.connection.set_keyspace(connection_config['database'])

    def __setup_database(self, config):
        # Create the keyspace
        self.connection.execute(f'''
        CREATE KEYSPACE IF NOT EXISTS {config['database']} with replication = {{
            'class':'SimpleStrategy','replication_factor': {config['replication_factor']}
        }};
        ''')
        self.connection.set_keyspace(config['database'])
        self.connection.execute(f'''
        CREATE TABLE IF NOT EXISTS order_payment_status (
            order_id uuid PRIMARY KEY,
            status varchar,
            amount int
        );
        ''')

    def insert_payment_status(self, order_id, status, amount):
        try:
            self.connection.execute('''
               INSERT INTO order_payment_status (order_id, status, amount)
               VALUES (%s, %s, %s);
               ''', (order_id, status, amount))
        except Exception as e:
            raise DatabaseException(e)

    def set_payment_status(self, order_id, status):
        try:
            self.connection.execute('''
                UPDATE order_payment_status 
                SET status = %s
                WHERE order_id = %s;
                ''', (status, order_id))
        except Exception as e:
            raise DatabaseException(e)

    def get_payment(self, order_id):
        try:
            results = self.connection.execute('''
                SELECT status, amount FROM order_payment_status
                WHERE order_id = %s
                ''', (order_id,))
            row = results.one()
            if row is None:
                return None, None
            else:
                return row.status, row.amount
        except Exception as e:
            raise DatabaseException(e)
