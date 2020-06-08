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
                                              password=connection_config['password']) \
            if 'user' in connection_config else None
        cluster = Cluster([connection_config['host']], auth_provider=auth_provider)
        self.connection = cluster.connect()
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
        self.connection.set_keyspace(config['database'])
        self.connection.execute(f'''
        CREATE TABLE IF NOT EXISTS stock (
            item_id uuid PRIMARY KEY,
            price int
        );
        ''')
        self.connection.execute(f'''
        CREATE TABLE IF NOT EXISTS stock_counter (
            item_id uuid PRIMARY KEY,
            amount counter
        );
        ''')

    def find_stock(self, item_id):
        price = self.connection.execute(f'''
        SELECT price FROM stock
        WHERE item_id = %s;
        ''', (item_id,)).one()
        amount = self.get_stock(item_id)
        if price is None or amount is None:
            return None
        else:
            return amount[0], price[0]

    def stock_subtract(self, item_id, number):
        res = self.connection.execute(f'''
               UPDATE stock_counter
               SET amount = amount - %s
               WHERE item_id = %s AND amount >= %s;
               ''', (number, item_id, number)).one()

        return res.applied

    def stock_add(self, item_id, number):
        res = self.connection.execute(f'''
               UPDATE stock_counter
               SET amount = amount + %s
               WHERE item_id = %s;
               ''', (number, item_id)).one()

        return res.applied

    def create_stock(self, price):
        item_id = uuid.uuid4()
        self.connection.execute(f'''
                INSERT INTO stock (item_id, price)
                VALUES (%s, %s);
                ''', (item_id, price))
        self.connection.execute(f'''
                UPDATE stock_counter 
                SET amount = amount + 0
                WHERE item_id = %s;
                ''', (item_id,))
        return str(item_id)

    def get_stock(self, item_id):
        return self.connection.execute(f'''
               SELECT amount FROM stock_counter
               WHERE item_id = %s;
               ''', (item_id,)).one()

    def batch_subtract(self, items):
        log = []
        # Subtract all items.
        for item_id in items:
            success = self.stock_subtract(item_id, 1)
            if success:
                log.append(item_id)
            else:
                # Re-add all succeeded subtracted items.
                for l in log:
                    self.stock_add(l, 1)
                return False
        return True
