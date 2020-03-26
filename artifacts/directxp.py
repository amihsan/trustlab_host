###############################################
# Direct Experience
# The tag values in the logfiles are combined to the Direct XP via the median

from trustlab.lab.config import Logging


def direct_experience(current_agent, other_agent):
    history_name = current_agent + "_history.txt"
    history_path = Logging.LOG_PATH / history_name
    with open(history_path.absolute(), "r+") as history_file:
        # getting all history values of the agent respective to the other agent
        history = [float(entry.split(" ")[-1]) for entry in history_file.readlines() if entry.split(" ")[-2] == other_agent]
        # calculate direct experience
        direct_xp = sum(history)/len(history) if len(history) > 0 else 0.00
    return direct_xp
