from datetime import datetime
from os.path import dirname, abspath
from pathlib import Path
from random import randint

# path variables
PROJECT_PATH = Path(abspath(dirname(__name__)))
LOG_PATH = PROJECT_PATH / 'log'

# buffer size for TCP connections
BUFFER_SIZE = 2048

# determines the max size of one websocket message in bytes for potential chunked websocket messages
WEBSOCKET_MAX = 900000  # tested this limit 990000 seems too large for supervisor side

# aTLAS Version for check at supervisor <-> director connection
ATLAS_VERSION = "v 0.0.1"

TIME_MEASURE = True


def create_chunked_transfer_id():
    """
    Creates a new ID for chunked transfer within with datetime pattern plus 3 digit random int,
    e.g. '2021-05-18_16-37-54_383'.

    :return: new chunked transfer ID
    :rtype: str
    """
    return f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{randint(0, 999):0=3d}'
