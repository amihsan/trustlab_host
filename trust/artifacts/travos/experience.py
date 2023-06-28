from loggers.basic_logger import BasicLogger
from models import Scale
from scipy.stats import truncnorm
from scipy.stats import beta
from scipy.integrate import quad
from datetime import datetime


def experience(agent, other_agent, resource_id, scale, logger):
    """
    Calculate the direct experience value from the agent's history about other agents.

    :param agent: The agent which calculates the trust. (start of relationship)
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param resource_id: The URI of the resource which is evaluated.
    :param scale: The Scale object to be used by the agent.
    :param logger: The logger object to be used by the agent.
    :return: Direct experience value from agent about other agents.
    """
    history_value = None

    history_lines = logger.read_lines_from_agent_history(agent)

    for item in history_lines:
        if item['other_agent'] == other_agent:
            history_value = float(item['trust_value'])
            print(history_value)
            break

    # Convert history value to a tuple of successful and unsuccessful past interactions
    history_outcome = create_history_tuple(history_value)
    print(history_outcome)

    # Calculate direct trust value
    m = history_outcome[0] + 1
    n = history_outcome[1] + 1
    direct_xp = m / (m + n)
    print(direct_xp)
    # confidence_value = calculate_confidence_value(direct_xp, history_outcome)
    error_threshold = 0.2
    confidence_value = beta_integral(direct_xp - error_threshold, direct_xp + error_threshold, m, n) / beta_integral(0, 1, m, n)
    print(confidence_value)

    return direct_xp


def create_history_tuple(mean):
    std_dev = 0.10
    lower_bound = 0.0
    upper_bound = 1.0
    cooperation_threshold = 0.5
    success = 0
    unsuccess = 0

    dist = truncnorm((lower_bound - mean) / std_dev, (upper_bound - mean) / std_dev, loc=mean, scale=std_dev)

    samples = dist.rvs(size=10)

    for value in samples:
        if value > cooperation_threshold:
            success += 1
        else:
            unsuccess += 1

    history = (success, unsuccess)
    return history


def beta_integral(lower_limit, upper_limit, alpha, beta_):
    dist = beta(alpha, beta_)
    pdf = lambda x: dist.pdf(x)
    integral, _ = quad(pdf, lower_limit, upper_limit)
    return integral

