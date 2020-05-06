from setup import setup_app

# This contains the logic for running the application in production mode
# using the uwsgi server. The config file used is "config.wsgi.py".

_, app = setup_app()
