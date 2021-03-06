import abc


class DatabaseException(Exception):
    """A generic exception to encapsulate both cassandra and postgres
    exceptions"""
    pass


class Database(object):
    """Generic Database object, every different database connection should
    implement these functions."""
    __metaclass__ = abc.ABCMeta

    DATABASE: str
    connection: any

    @abc.abstractmethod
    def connect(self, config, setup):
        pass

    @abc.abstractmethod
    def insert_payment_status(self, order_id, status, amount):
        pass

    @abc.abstractmethod
    def set_payment_status(self, order_id, status):
        pass

    @abc.abstractmethod
    def get_payment(self, order_id):
        pass
