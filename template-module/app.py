from setup import setup_app

# This contains the logic for running the application in development mode.
# It uses the default flask development server and should not be used in
# production. The config file used is "config.py".

config, app = setup_app()
if config['dev'] is not None:
    app.run(host=config['dev']['host'], port=config['dev']['port'])
