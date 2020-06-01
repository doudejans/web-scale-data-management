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
            amount int,
            price int
        );
        ''')
        self.connection.execute(f'''
       CREATE TABLE IF NOT EXISTS stock_log (
           transaction_id uuid PRIMARY KEY,
           item_id uuid,
           amount int,
           status varchar
       );
       ''')

    def find_stock(self, item_id):
        res = self.connection.execute(f'''
        SELECT amount, price FROM stock
        WHERE item_id = %s;
        ''', (item_id,)).one()
        return None if res is None else res.amount, res.price

    def stock_subtract(self, item_id, number):
        # create transaction ID
        transaction_id = uuid.uuid4()

        # get current stock amount
        res = self.get_stock(item_id)
        if res is None:
            return False
        amount = res.amount
        # check if subtracted number is too high
        if number > amount:
            return False
        # set new stock amount
        subtraction = amount - number
        res = self.connection.execute(f'''
               UPDATE stock
               SET amount = %s
               WHERE item_id = %s
               IF amount = %s;
               ''', (subtraction, item_id, amount)).one()

        # create transaction
        self.connection.execute(f'''
                INSERT INTO stock_log (transaction_id, item_id, amount, status)
                VALUES (%s, %s, %s, %s);
                ''', (transaction_id, item_id, -number, "commit"))

        return res.applied, transaction_id

    def stock_add(self, item_id, number):
        # create transaction ID
        transaction_id = uuid.uuid4()

        # get current stock amount
        res = self.get_stock(item_id)
        if res is None:
            return False
        amount = res.amount
        # set new stock amount
        addition = amount + number
        res = self.connection.execute(f'''
               UPDATE stock
               SET amount = %s
               WHERE item_id = %s
               IF amount = %s;
               ''', (addition, item_id, amount)).one()

        # create transaction
        self.connection.execute(f'''
                      INSERT INTO stock_log (transaction_id, item_id, amount, status)
                      VALUES (%s, %s, %s, %s);
                      ''', (transaction_id, item_id, number, "Commit"))

        return res.applied, transaction_id

    def create_stock(self, price):
        item_id = uuid.uuid4()
        self.connection.execute(f'''
                INSERT INTO stock (item_id, amount, price)
                VALUES (%s, 0, %s);
                ''', (item_id, price))
        return str(item_id)

    def rollback(self, transaction_id):
        # get stock id and amount from the transaction log
        res = self.get_log(transaction_id)
        if res is None or res.status == "Rollback":
            return False
        amount = res.amount
        item_id = res.item_id

        print(amount)
        if amount > 0:
            rollback = self.stock_subtract(item_id, amount)
        else:
            rollback = self.stock_add(item_id, -amount)

        # Set transaction log to rollback.
        if rollback:
            self.connection.execute(f'''
              UPDATE stock_log
              SET status = %s
              WHERE transaction_id = %s
              ''', ("Rollback", transaction_id)).one()
            return True
        else:
            return False

    def get_stock(self, item_id):
        return self.connection.execute(f'''
               SELECT amount FROM stock
               WHERE item_id = %s;
               ''', (item_id,)).one()

    def get_log(self, transaction_id):
        return self.connection.execute(f'''
               SELECT item_id, amount, status FROM stock_log
               WHERE transaction_id = %s;
               ''', (transaction_id,)).one()
