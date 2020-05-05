# Template Module

*This module was created to define a common layout to use during
development as the different microservices (outlined in the main
`README`) will be developed by different people at the same time.*

- You can duplicate this folder and rename it to your microservice.
- If you are using PyCharm, make sure to mark that directory as `sources root`
(right click on the folder -> `Mark Directory As` -> `Sources Root`). This
will prevent import errors you might have later on.
- The app can be run in two ways:
  - During development using `app.py`

    ```python app.py```

  - **@doudejans** For production/deployment using `wsgi.py`

    ```uwsgi --http :5000 --wsgi-file wsgi.py --callable app```

  *Note: These different modes make use of a different configuration file
  instead of program arguments (I tried that first) as in wsgi mode it does
  not seem possible to provide arguments.*

- You define the routes for your service in `routes.py` which has access to a
`db` object. This database is is either a Cassandra or Postgres database which
 is abstracted away such that the application can easily switch between the
 two using a configuration file.

   Look at the comments in this file and the example route on how to add your
   own routes.

- If you need a function on the database, say to create a user, you can add an
 abstract implementation of it to `database/database.py`. This then forces you
 to add an actual implementation of this function in the supported databases:
 `database/postgres.py` and `database/cassandra.py`. By adhering to this
 abstraction the app can run on either database, which is required for the
 comparision.

   In this file you'll need to fill in the `__setup_database` function to set
   up the correct tables and as specified before the functions to store
   /retrieve the data you need from these tables.

## Production
*This is mostly a note to **@doudejans***

In production we should not be using the default Flask web server, instead we
use [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) which is written in
C and should be rather fast.
We set it up as defined in the
[Flask documentation](https://flask.palletsprojects.com/en/1.1.x/deploying/uwsgi/) 
and [uWSGI documentation](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html).

I've set up the template to allow for using uWSGI so it should be a trivial
task to connect it to an nginx webserver.
