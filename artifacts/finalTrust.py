# The final trust result is combined through the sum of the
# values in the log file and the corresponding weight given by the scenario file
from config import Logging


def final_trust(current_agent, other_agent):
    file_name = current_agent + "_trust_log.txt"
    log_path = Logging.LOG_PATH / file_name
    with open(log_path.absolute(), "r+") as agent_trust_file:
        trust_values = []
        for line in agent_trust_file.readlines():
            if line.split(" ")[-2] == other_agent:
                trust_values.append(float(line.split(" ")[-1]))
    trust = sum(trust_values) / len(trust_values) if len(trust_values) > 0 else 0.00
    return trust


