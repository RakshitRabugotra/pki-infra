import datetime
import uuid

def now():
    return datetime.datetime.now()

def timestamp(format: str = None):
    """
    Generates a timestamp of now
    """
    return now().strftime(format or "%d-%m-%Y-%H-%M-%S")


def get_id():
    return uuid.uuid4().hex