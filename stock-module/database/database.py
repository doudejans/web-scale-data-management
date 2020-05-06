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
    def retrieve_version(self):
        pass

    @abc.abstractmethod
    def get_availability(self, item_id):
        pass

    @abc.abstractmethod
    def stock_subtract(self, item_id, number):
        pass

    @abc.abstractmethod
    def stock_add(self, item_id, number):
        pass

    @abc.abstractmethod
    def create_stock(self):
        pass
