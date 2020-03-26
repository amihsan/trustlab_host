from pathlib import Path
import os
from datetime import datetime


class ServerStatus:
    SCENARIO = None
    SHUTDOWN = False

    @staticmethod
    def set_scenario(scenario):
        ServerStatus.SCENARIO = scenario

    @staticmethod
    def shutdown_server():
        ServerStatus.SHUTDOWN = True


class Logging:
    LOG_PATH = Path("trustlab/lab/log/")
    if not LOG_PATH.is_dir():
        os.mkdir(LOG_PATH.absolute())

    @staticmethod
    def new_log_path():
        folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        Logging.LOG_PATH = Path("trustlab/lab/log/" + folder_name + "/")
        os.mkdir(Logging.LOG_PATH.absolute())


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")




