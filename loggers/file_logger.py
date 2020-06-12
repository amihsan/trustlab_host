from pathlib import Path
import os
from loggers.basic_logger import BasicLogger


class FileLogger(BasicLogger):
    LOG_PATH = Path("log/")
    if not LOG_PATH.is_dir():
        os.mkdir(LOG_PATH.absolute())

    def log_observation(self):
        pass

    def write_to_agent_history(self, agent, other_agent, history_value):
        history_name = agent + "_history.txt"
        history_path = self.log_path / history_name
        with open(history_path.absolute(), "ab+") as history_file:
            history_file.write(BasicLogger.get_current_time() + ', history trust value from: ' + other_agent + ' ' +
                               str(history_value) + '\n')

    def write_bulk_to_agent_history(self, agent, history):
        history_name = agent + "_history.txt"
        history_path = self.log_path / history_name
        with open(history_path.absolute(), "ab+") as history_file:
            for other_agent, history_value in history.items():
                history_file.write(BasicLogger.get_current_time() + ', history trust value from: ' + other_agent + ' ' +
                                   str(history_value) + '\n')

    def __init__(self, scenario_run_id):
        super().__init__()
        split_index = len(scenario_run_id.split("_")[0]) + 1  # number to cut constant of runId -> 'scenarioRun_'
        self.folder_name = scenario_run_id[split_index:]
        self.log_path = Path("log/" + self.folder_name + "/")
        if not self.log_path.is_dir():
            os.mkdir(self.log_path.absolute())

