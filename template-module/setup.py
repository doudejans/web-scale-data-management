import routes
from config import retrieve_config
from database.database import Database
from database.postgres import PostgresDB
from database.cassandra import CassandraDB

APPLICATION_NAME = "microservice"


def setup_app():
    """
    Application setup code based on configuration file.

    This logic is located here as it is shared between the development and
    wsgi mode.
    """
    config = retrieve_config(APPLICATION_NAME)

    database_config = config['database']

    print(f"Starting {APPLICATION_NAME}")
    print(f" - Using a {database_config['type']} database.")
    db: Database = PostgresDB() if database_config['type'] == "postgres" \
        else CassandraDB()
    should_setup = database_config['setup']

    db.connect(database_config, should_setup)

    app = routes.create_app(db)
    return config, app
