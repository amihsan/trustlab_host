from pathlib import Path
from os.path import dirname, abspath

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
