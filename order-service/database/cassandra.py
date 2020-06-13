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
                                              password=connection_config['password'])\
            if 'user' in connection_config else None
        cluster = Cluster([connection_config['host']], auth_provider=auth_provider)
        self.connection = cluster.connect()
        if setup:
            self.__setup_database(connection_config)
        self.connection.set_keyspace(connection_config['database'])
        self.add_order_query = self.connection.prepare('''
        INSERT INTO orders (order_id, user_id) VALUES (?, ?)
        ''')
        self.delete_order_query = self.connection.prepare('''
        DELETE FROM orders WHERE order_id = ?
        ''')
        self.get_order_query1 = self.connection.prepare('''
        SELECT user_id FROM orders WHERE order_id = ?
        ''')
        self.get_order_query2 = self.connection.prepare('''
        SELECT item_id, amount FROM order_items WHERE order_id = ?
        ''')
        self.add_item_to_order_query1 = self.connection.prepare('''
        SELECT amount FROM order_items WHERE order_id = ? AND item_id = ?
        ''')
        self.add_item_to_order_query2 = self.connection.prepare('''
        SELECT * from orders WHERE order_id = ?
        ''')
        self.add_item_to_order_query3 = self.connection.prepare('''
        INSERT INTO order_items (order_id, item_id, amount) VALUES (?, ?, ?)
        ''')
        self.add_item_to_order_query4 = self.connection.prepare('''
        UPDATE order_items SET amount = ? WHERE order_id = ? AND item_id = ?
        IF amount = ?
        ''')
        self.remove_item_from_order_query1 = self.connection.prepare('''
        SELECT amount FROM order_items WHERE order_id = ? AND item_id = ?
        ''')
        self.remove_item_from_order_query2 = self.connection.prepare('''
        UPDATE order_items SET amount = ? WHERE order_id = ? AND item_id = ?
        IF amount = ?
        ''')


    def add_order(self, order_id, user_id):
        self.connection.execute(self.add_order_query, (order_id, user_id))

    def delete_order(self, order_id):
        self.connection.execute(self.delete_order_query, (order_id, ))

    def get_order(self, order_id):
        results = self.connection.execute(self.get_order_query1, (order_id, ))
        row = results.one()

        if row:
            user_id = row[0]
            items = self.connection.execute(self.get_order_query2, (order_id, ))

            return {
                'order_id': order_id,
                'user_id': user_id,
                'items': [item_id for item in items for item_id in [item[0] for _ in range(0, item[1])]]
            }
        else:
            return None

    def add_item_to_order(self, order_id, item_id):
        results = self.connection.execute(self.add_item_to_order_query1, (order_id, item_id))

        if results.one() is None:
            exists = self.connection.execute(self.add_item_to_order_query2, (order_id, ))

            if not exists.one():
                return False

            self.connection.execute(self.add_item_to_order_query3, (order_id, item_id, 1))
            return True
        else:
            amount = results.one()[0]
            updated_amount = amount + 1

            result = self.connection.execute(self.add_item_to_order_query4, (updated_amount, order_id, item_id, amount))

            return result.was_applied

    def remove_item_from_order(self, order_id, item_id):
        results = self.connection.execute(self.remove_item_from_order_query1, (order_id, item_id))

        if results.one() is None:
            return False

        amount = results.one()[0]

        if amount > 0:
            updated_amount = amount - 1
            result = self.connection.execute(self.remove_item_from_order_query2, (updated_amount, order_id, item_id, amount))

            return result.was_applied

        return False



    def __setup_database(self, config):
        # Create the keyspace
        self.connection.execute(f'''
        CREATE KEYSPACE IF NOT EXISTS {config['database']} with replication = {{
            'class':'SimpleStrategy','replication_factor':1
        }};
        ''')
        self.connection.set_keyspace(config['database'])
        self.connection.execute('''
        CREATE TABLE IF NOT EXISTS orders (order_id uuid, user_id uuid, PRIMARY KEY (order_id));
        ''')

        self.connection.execute('''
        CREATE TABLE IF NOT EXISTS order_items (order_id uuid, item_id uuid, amount int, PRIMARY KEY (order_id, item_id)) WITH CLUSTERING ORDER BY (item_id DESC);
        ''')
