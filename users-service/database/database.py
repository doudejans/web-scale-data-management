import abc


class Database(object):
    """Generic Database object, every different database connection should
    implement these functions."""
    __metaclass__ = abc.ABCMeta

    DATABASE: str
    connection: any

    @abc.abstractmethod
    def connect(self, config, setup):
        pass

    # TODO: Define the required functions for your db here...
    @abc.abstractmethod
    def retrieve_version(self):
        pass
