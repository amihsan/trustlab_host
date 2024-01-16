import ast


def experience(agent, other_agent, logger):
    """
        Calculate the direct experience trust value from the agent's history about other agents.

        :param agent: The agent which calculates the trust. (start of relationship)
        :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
        :type other_agent: str
        :param logger: The logger object to be used by the agent.
        :return: Both the trust value and history tuple.
        :rtype:tuple
        """
    history_lines = logger.read_lines_from_agent_history(agent)
    # print(history_lines)

    # from agent history log find out the direct trust value (history tuple) by filtering them
    # based on other agent.
    for item in history_lines:
        if item['other_agent'] == other_agent:
            # history tuple as a string
            history_string = ast.literal_eval(item['trust_value'])
            # print(history)

            # convert string to tuple
            history = ast.literal_eval(history_string)
            # print(f"History tuple: {history}")

            # find out direct experience trust value
            direct_trust = calculate_direct_trust(history)
            # print(f"Experience value: {direct_trust}")
            break

    return direct_trust, history


# Calculate direct expected experience trust value Beta PDF
def calculate_direct_trust(history):
    # determine no of successful (m) and no of unsuccessful (n) interactions from history tuple
    m = history[0]
    n = history[1]

    # shape parameter for pdf
    alpha = m + 1
    beta = n + 1

    direct_trust = alpha / (alpha + beta)

    return direct_trust
