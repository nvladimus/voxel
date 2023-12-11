import inspect

class BaseFilterWheel:

    def __init__(self):
        self.filter_list = list()

    def get_index(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def set_index(self, filter_name: str, wait=True):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass