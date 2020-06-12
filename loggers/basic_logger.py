from abc import ABC, abstractmethod
from datetime import datetime


class BasicLogger(ABC):
    @abstractmethod
    def log_observation(self):
        pass

    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __init__(self):
        pass

