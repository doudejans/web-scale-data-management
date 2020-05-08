import uuid

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, Session

from database.database import Database


# This file connects to the cassandra database, it should expose the same
# functions as the other database models (db_postgres.py).

class CassandraDB(Database):
    DATABASE = "CASSANDRA"
    connection: Session = None

    def connect(self, config, setup=False):
        connection_config = config['connection']
        auth_provider = PlainTextAuthProvider(username=connection_config['user'],
                                              password=connection_config['password']) \
            if 'user' in connection_config else None
        cluster = Cluster(auth_provider=auth_provider)
        self.connection = cluster.connect()
        # TODO: Add specific connection code, if needed.
        if setup:
            self.__setup_database(connection_config)
        self.connection.set_keyspace(connection_config['database'])

    def __setup_database(self, config):
        # Create the keyspace
        self.connection.execute(f'''
        CREATE KEYSPACE IF NOT EXISTS {config['database']} with replication = {{
            'class':'SimpleStrategy','replication_factor':1
        }};
        ''')
        self.connection.set_keyspace(config['keyspace'])
        self.connection.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            user_id uuid PRIMARY KEY,
            credit int
        );
        ''')

    def retrieve_version(self):
        # This is an example for a query. The same query, with the same function
        # name, parameters and return type, should be implemented for the other
        # database.
        return self.connection.execute("""
          SELECT release_version FROM system.local
        """).one()

    def create_user(self):
        user_id = str(uuid.uuid4())
        self.connection.execute(f'''
        INSERT INTO users (user_id, credit)
        VALUES ({user_id}, 0);
        ''')
        return user_id

    def remove_user(self, user_id):
        res = self.connection.execute(f'''
        DELETE FROM users
        WHERE user_id = {user_id}
        IF EXISTS;
        ''').one()
        return res.applied

    def get_credit(self, user_id):
        res = self.connection.execute(f'''
        SELECT credit FROM users
        WHERE user_id = {user_id};
        ''').one()
        return None if res is None else res.credit

    def credit_add(self, user_id, amount):
        # get current credit
        res = self.connection.execute(f'''
        SELECT credit FROM users
        WHERE user_id = {user_id};
        ''').one()
        if res is None:
            return False
        credit = res.credit
        # set new credit
        res = self.connection.execute(f'''
        UPDATE users
        SET credit = {credit + amount}
        WHERE user_id = {user_id}
        IF credit = {credit};
        ''').one()
        return res.applied

    def credit_subtract(self, user_id, amount):
        # get current credit
        res = self.connection.execute(f'''
        SELECT credit FROM users
        WHERE user_id = {user_id};
        ''').one()
        if res is None:
            return False
        credit = res.credit
        # check balance
        if amount > credit:
            return False
        # set new credit
        res = self.connection.execute(f'''
        UPDATE users
        SET credit = {credit - amount}
        WHERE user_id = {user_id}
        IF credit = {credit};
        ''').one()
        return res.applied
