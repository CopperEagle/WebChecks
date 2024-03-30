"""Provides the singleton decorator."""

def singleton(cls):
    """Avoids creating more than a single object for this class."""
    instances = {}

    def getinstance(*args):
        if cls not in instances:
            instances[cls] = cls(*args)
        return instances[cls]
    return getinstance
