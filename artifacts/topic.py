###############################################
# Topic check

from scenario_manager import Logging
from artifacts.directxp import direct_experience


def topic(current_agent, other_agent, current_topic):
    topic_name = current_agent + "_topic.txt"
    topic_path = Logging.LOG_PATH / topic_name
    with open(topic_path.absolute(), "r+") as topic_file:
        # getting all topic values of the agent respective to the other agent and the current topic
        topic_values = [float(entry.split(" ")[-1]) for entry in topic_file.readlines() if entry.split(" ")[-3] == other_agent and entry.split(" ")[-2] == current_topic]
        # calculate topic trust
        topic_value = sum(topic_values) / len(topic_values) if len(topic_values) > 0 else 0.00
    return topic_value


