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
    def add_order(self, order_id, user_id):
        pass

    @abc.abstractmethod
    def delete_order(self, order_id):
        pass

    @abc.abstractmethod
    def get_order(self, order_id):
        pass
