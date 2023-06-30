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
    history_value = None

    history_lines = logger.read_lines_from_agent_history(agent)

    for item in history_lines:
        if item['other_agent'] == other_agent:
            history_value = float(item['trust_value'])
            print(f"history value:{history_value}")

            # Convert history value to a tuple of successful and unsuccessful past interactions by using
            # truncated normal distribution
            std_dev = 0.10
            lower_bound = 0.0
            upper_bound = 1.0
            cooperation_threshold = 0.5
            sample_size = 10

            # setting mean = history_value in dist formula
            # dist = truncnorm((lower_bound - mean) / std_dev, (upper_bound - mean) / std_dev, loc=mean, scale=std_dev)

            dist = truncnorm((lower_bound - history_value) / std_dev, (upper_bound - history_value) / std_dev,
                             loc=history_value, scale=std_dev)

            samples = dist.rvs(size=10)

            success = sum(value > cooperation_threshold for value in samples)
            unsuccess = sample_size - success

            history = (success, unsuccess)

            # history_outcome = create_history_tuple(history_value)
            print(f"history tuple:{history}")

            # Calculate direct expected trust value using beta pdf
            # shape parameter
            x = history[0] + 1
            y = history[1] + 1

            # calculate expected trust value
            direct_trust = x / (x + y)
            print(f"experience value:{direct_trust}")
            return direct_trust, history
