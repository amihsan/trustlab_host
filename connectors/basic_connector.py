from abc import ABC, abstractmethod


class BasicConnector(ABC):
    @abstractmethod
    def register_at_director(self):
        pass

    def __init__(self, director_hostname):
        self.director_hostname = director_hostname

