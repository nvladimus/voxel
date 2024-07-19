
class UpdatingProperty(property):
    """Class that signals a property that needs to be updated continously"""

    def __init__(self,  fget, fset=None, fdel=None, currently_updating=False):

        super().__init__(fget=fget, fset=fset, fdel=fdel)

        self.currently_updating = currently_updating
