from loggers.basic_logger import BasicLogger
from models import Scale
from scipy.stats import truncnorm
from scipy.stats import beta
from scipy.integrate import quad
from datetime import datetime


def experience(agent, other_agent, resource_id, scale, logger, discovery, recency_limit):
    """
        Calculate the direct experience value from the agent's history about other agents.

        :param agent: The agent which calculates the trust. (start of relationship)
        :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
        :type other_agent: str
        :param resource_id: The URI of the resource which is evaluated.
        :param scale: The Scale object to be used by the agent.
        :param logger: The logger object to be used by the agent.
        :param discovery: Addresses of all agents within the scenario.
        :type discovery: dict
        :param recency_limit: A datetime object which is used for "forgetting" old history entries
        :type recency_limit: datetime
        :return: Direct experience value from agent about other agents.
        """
    history_lines = logger.read_lines_from_agent_history(agent)

    for item in history_lines:
        if item['other_agent'] == other_agent:
            history_value = float(item['trust_value'])
            print(f"History value: {history_value}")

            history = calculate_history_tuple(history_value)
            print(f"History tuple: {history}")

            direct_trust = calculate_direct_trust(history)
            print(f"Experience value: {direct_trust}")

            return direct_trust, history


# Convert history value to a tuple of successful and unsuccessful past interactions by using
# truncated normal distribution
def calculate_history_tuple(history_value):
    std_dev = 0.10
    lower_bound = 0.0
    upper_bound = 1.0
    cooperation_threshold = 0.5
    sample_size = 10

    dist = truncnorm(
        (lower_bound - history_value) / std_dev,
        (upper_bound - history_value) / std_dev,
        loc=history_value,
        scale=std_dev
    )

    samples = dist.rvs(size=sample_size)

    success = sum(value > cooperation_threshold for value in samples)
    unsuccess = sample_size - success

    history = (success, unsuccess)

    return history


# Calculate direct expected trust value using beta pdf
def calculate_direct_trust(history):
    # shape parameter
    x = history[0] + 1
    y = history[1] + 1

    direct_trust = x / (x + y)

    return direct_trust

