import yaml


def read_config(file="config/config.yml"):
    """Reads a configuration file"""
    with open(file, "r") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as e:
            print(e)
    return config
