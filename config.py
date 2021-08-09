from pathlib import Path
from os.path import dirname, abspath

# path variables
PROJECT_PATH = Path(abspath(dirname(__name__)))
LOG_PATH = PROJECT_PATH / 'log'

# aTLAS Version for check at supervisor <-> director connection
ATLAS_VERSION = "v 0.0.1"
