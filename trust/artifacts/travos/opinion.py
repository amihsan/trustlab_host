import ast
from loggers.basic_logger import BasicLogger


def look_for_opinions(agent, other_agent, logger, discovery):
    """
    Calculate opinion trust value on other agent by collecting opinions from third parties (other available agents).

    :param agent: The agent which calculates the opinion.
    :type agent: str
    :param other_agent: The other agent for which the opinion value is calculated.
    :type other_agent: str
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The Opinion trust value.
    :rtype: float or int
    """
    # store the list of available opinion provider agent
    opinion_provider_agent = [provider_agent for provider_agent in discovery
                              if provider_agent != agent and provider_agent != other_agent]

    # store the opinion tuple collected from opinion provider agent list
    opinion_outcome = []

    # collect  opinion tuple from opinion provider agent
    for agent in opinion_provider_agent:
        # print(f"provider agent:{agent}")
        agent_history = logger.read_lines_from_agent_history(agent)
        # print(f"{agent} history:{agent_history}")
        for item in agent_history:
            if item['other_agent'] == other_agent:
                # Collect trust value as string
                history_string = ast.literal_eval(item['trust_value'])
                # Converts string to tuple
                history = ast.literal_eval(history_string)

                opinion_outcome.append(history)
                break

    # Calculate M(successful) and N(unsuccessful) (from opinion_outcome)
    M = sum(value[0] for opinion in opinion_outcome for value in [opinion])
    N = sum(value[1] for opinion in opinion_outcome for value in [opinion])

    # Calculate shape parameter alpha and beta
    alpha = M + 1
    beta = N + 1

    # Calculate new opinion trust  value for other_agent
    opinion_trust_value = alpha / (alpha + beta)

    print(f"opinion provider : {opinion_provider_agent}")
    print(f"Opinion tuple:{opinion_outcome}")
    print(f"Shape parameter for opinion: ({alpha}, {beta})")
    print(f"The opinion trust value for {other_agent} is: {opinion_trust_value}")

    return opinion_trust_value
