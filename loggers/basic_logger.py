from abc import ABC, abstractmethod
from datetime import datetime


class BasicLogger(ABC):
    @abstractmethod
    def write_to_agent_history(self, agent, other_agent, history_value):
        pass

    @abstractmethod
    def write_bulk_to_agent_history(self, agent, history):
        pass

    @abstractmethod
    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value):
        pass

    @abstractmethod
    def write_bulk_to_agent_topic_trust(self, agent, topic_trust):
        pass

    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __init__(self, scenario_run_id, semaphore):
        self.scenario_run_id = scenario_run_id
        self.semaphore = semaphore

