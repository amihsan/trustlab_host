from pathlib import Path
import os
from loggers.basic_logger import BasicLogger


class FileLogger(BasicLogger):
    LOG_PATH = Path("log/")
    if not LOG_PATH.is_dir():
        os.mkdir(LOG_PATH.absolute())

    def write_to_agent_history(self, agent, other_agent, history_value):
        with self.semaphore:
            file_name = agent + "_history.txt"
            path = self.log_path / file_name
            with open(path.absolute(), "ab+") as history_file:
                history_file.write(BasicLogger.get_current_time() + ', history trust value from: ' + other_agent + ' ' +
                                   str(history_value) + '\n')

    def write_bulk_to_agent_history(self, agent, history):
        with self.semaphore:
            file_name = agent + "_history.txt"
            path = self.log_path / file_name
            with open(path.absolute(), "ab+") as history_file:
                for other_agent, history_value in history.items():
                    history_file.write(BasicLogger.get_current_time() + ', history trust value from: ' + other_agent
                                       + ' ' + str(history_value) + '\n')

    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value):
        with self.semaphore:
            file_name = agent + "_topic.txt"
            topic_path = self.log_path / file_name
            with open(topic_path.absolute(), "ab+") as topic_file:
                # TODO topic not always required to be single word
                topic_file.write(BasicLogger.get_current_time() + ', topic trust value from: ' + other_agent +
                                 ' ' + topic + ' ' + str(topic_value) + '\n')

    def write_bulk_to_agent_topic_trust(self, agent, topic_trust):
        with self.semaphore:
            file_name = agent + "_topic.txt"
            topic_path = self.log_path / file_name
            with open(topic_path.absolute(), "ab+") as topic_file:
                for other_agent, topic_dict in topic_trust.items():
                    if topic_dict:
                        for topic, topic_value in topic_dict.items():
                            # TODO topic not always required to be single word
                            topic_file.write(BasicLogger.get_current_time() + ', topic trust value from: ' + other_agent
                                             + ' ' + topic + ' ' + str(topic_value) + '\n')

    def __init__(self, scenario_run_id, semaphore):
        super().__init__(scenario_run_id, semaphore)
        split_index = len(scenario_run_id.split("_")[0]) + 1  # index to cut constant of runId -> 'scenarioRun_'
        self.folder_name = scenario_run_id[split_index:]
        self.log_path = Path("log/" + self.folder_name + "/")
        if not self.log_path.is_dir():
            os.mkdir(self.log_path.absolute())

