from abc import ABC, abstractmethod


class BasicConnector(ABC):
    @abstractmethod
    def register_at_director(self, max_agents):
        pass

    @abstractmethod
    def set_max_agents(self, max_agents):
        pass

    @abstractmethod
    async def get_next_run(self):
        pass

    def __init__(self, director_hostname):
        self.director_hostname = director_hostname

