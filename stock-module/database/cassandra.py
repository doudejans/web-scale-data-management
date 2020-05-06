import uuid
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, Session
from database.database import Database


# This file connects to the cassandra database, it should expose the same
# functions as the other database models (db_postgres.py).

# noinspection SqlDialectInspection
class CassandraDB(Database):
    DATABASE = "CASSANDRA"
    connection: Session = None

    def connect(self, config, setup=False):
        connection_config = config['connection']
        auth_provider = PlainTextAuthProvider(username=connection_config['user'],
                                              password=connection_config['password'])\
            if 'user' in connection_config else None
        cluster = Cluster(auth_provider=auth_provider)
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
        self.connection.execute(f'''
        CREATE TABLE IF NOT EXISTS stock (
            item_id uuid PRIMARY KEY,
            amount int
        );
        ''')

    def retrieve_version(self):
        # This is an example for a query. The same query, with the same function
        # name, parameters and return type, should be implemented for the other
        # database.
        return self.connection.execute("""
          SELECT release_version FROM system.local
        """).one()

    def get_availability(self, item_id):
        res = self.connection.execute(f'''
        SELECT amount FROM stock
        WHERE item_id = {item_id};
        ''').one()
        return None if res is None else res.amount

    def stock_subtract(self, item_id, number):
        # get current stock amount
        res = self.connection.execute(f'''
               SELECT amount FROM stock
               WHERE item_id = {item_id};
               ''').one()
        if res is None:
            return False
        amount = res.amount
        # check if subtracted number is too high
        if number > amount:
            return False
        # set new stock amount
        res = self.connection.execute(f'''
               UPDATE stock
               SET amount = {amount - number}
               WHERE item_id = {item_id}
               IF amount = {amount};
               ''').one()
        return res.applied

    def stock_add(self, item_id, number):
        # get current stock amount
        res = self.connection.execute(f'''
                       SELECT amount FROM stock
                       WHERE item_id = {item_id};
                       ''').one()
        if res is None:
            return False
        amount = res.amount
        # set new stock amount
        res = self.connection.execute(f'''
                       UPDATE stock
                       SET amount = {amount + number}
                       WHERE item_id = {item_id}
                       IF amount = {amount};
                       ''').one()
        return res.applied

    def create_stock(self):
        item_id = str(uuid.uuid4())
        self.connection.execute(f'''
                        INSERT INTO stock (item_id, amount)
                        VALUES ({item_id}, 0);
                        ''')
        return item_id
