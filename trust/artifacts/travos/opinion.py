from datetime import datetime

from scipy.stats import truncnorm

from loggers.basic_logger import BasicLogger
from models import Scale
from .experience import experience


# Calculate opinion value based on opinion provider agent
def look_for_opinions(agent, other_agent, resource_id, scale, logger, discovery, recency_limit):
    """
    Get recommendations on other agent of third agents and average them to one recommendation value.

    :param agent: The agent which calculates the opinion.
    :type agent: str
    :param other_agent: The other agent for which the opinion value is calculated.
    :type other_agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :return: The Recommendation trust value.
    :rtype: float or int
    """
    # store the list of opinion provider
    opinion_provider_agent = [provider_agent for provider_agent in discovery
                              if provider_agent != agent and provider_agent != other_agent]

    opinion_collected = []
    opinion_history = []

    for agent in opinion_provider_agent:
        print(agent)
        agent_history = logger.read_lines_from_agent_history(agent)
        print(f"{agent} history:{agent_history}")
        for item in agent_history:
            if item['other_agent'] == other_agent:
                history_value = float(item['trust_value'])
                print(history_value)
                opinion_collected.append(history_value)

    for trust_value in opinion_collected:
        opinion_outcome = create_opinion_outcome(trust_value)
        opinion_history.append(opinion_outcome)

    # Calculate x(successful) and y(unsuccessful) (from opinion_history)
    x = sum(value[0] for opinion in opinion_history for value in [opinion])
    y = sum(value[1] for opinion in opinion_history for value in [opinion])

    # Calculate shape parameter alpha and beta
    alpha = x + 1
    beta = y + 1
    print(f"Shape parameter : ({alpha}, {beta})")

    # Calculate new opinion trust  value for other_agent
    opinion_trust_value = alpha / (alpha + beta)
    print(f"The new trust value for {other_agent} is: {opinion_trust_value}")
    return opinion_trust_value


    # direct_trust_value = experience(agent, other_agent, resource_id, scale, logger, discovery, recency_limit)
    #
    # if opinion_trust_value > direct_trust_value:
    #     print(f"opinion value is new trust value : {opinion_trust_value}")
    #     return opinion_trust_value


# Create opinion tuple from trust values provided by opinion provider agent
# by setting mean = trust value
def create_opinion_outcome(mean):
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

    opinion = (success, unsuccess)
    return opinion
