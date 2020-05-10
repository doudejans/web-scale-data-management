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

    @abc.abstractmethod
    def create_user(self):
        pass

    @abc.abstractmethod
    def remove_user(self, user_id):
        pass

    @abc.abstractmethod
    def get_credit(self, user_id):
        pass

    @abc.abstractmethod
    def credit_add(self, user_id, amount):
        pass

    @abc.abstractmethod
    def credit_subtract(self, user_id, amount):
        pass
