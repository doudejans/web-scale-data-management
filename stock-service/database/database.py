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

    @abc.abstractmethod
    def find_stock(self, item_id):
        pass

    @abc.abstractmethod
    def stock_subtract(self, item_id, number):
        pass

    @abc.abstractmethod
    def stock_add(self, item_id, number):
        pass

    @abc.abstractmethod
    def create_stock(self, price):
        pass

    @abc.abstractmethod
    def rollback(self, transaction_id):
        pass