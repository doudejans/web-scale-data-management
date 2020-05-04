# Web Scala Data Management Project
*Project work for IN4331 Web-scale Data Management.*

The project is defined as 4 microservices which together make up the
functionality of a simple order system.

The goal of the project is to compare
[Cassandra](https://cassandra.apache.org) (a wide-column database) against
[Postgres](https://www.postgresql.org) (Relational Database) with regards to
performance, scalability and consistency.

## Installation
- Make sure you have Python 3 installed (specifically tested with
`v3.8`).
- `Optional` Create a
[virtualenv](https://docs.python.org/3/library/venv.html) by running
the following command:

  `python3 -m venv .venv`

  And activate it by running

  `source .venv/bin/activate`

  In case you are developing in an IDE like PyCharm you might have to point it 
  to the virtual environment (it usually does this by itself though). You can
  do this by:
   - Opening the editor preferences
   - Go to the tab `Project: web-scale-data-management` (the name of the
   project might differ if you placed the project in a different folder)
   - Click `Python Interpreter`
   - Select the correct virtual env in the list (by looking at the directory in
  which they are placed)
   - if it is not there you can use the gear icon in the top right and press `add` -> given that you followed the instructions below you can add an `Existing environment` and point it to the folder where
  you created the environment.

- Install the requirements defined in the `requirements.txt` by running:

  `python3 -m pip install -r requirements.txt`.
