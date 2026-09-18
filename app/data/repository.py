from functools import lru_cache

from app.data.loader import load_support_tickets


@lru_cache(maxsize=1)
def get_support_tickets():
    """
    Return the support ticket dataset.

    The dataset is cached so repeated analytics requests
    do not reload the CSV from disk.
    """
    return load_support_tickets()
