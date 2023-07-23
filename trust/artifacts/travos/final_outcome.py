from trust.artifacts.travos.confidence import calculate_confidence_value
from trust.artifacts.travos.experience import experience
from trust.artifacts.travos.opinion import look_for_opinions
from loggers.basic_logger import BasicLogger


def final_interaction_outcome(agent, other_agent, resource_id, logger, discovery):
    """
      Get Final Binary outcome of an interaction between agent and other agent.

      :param agent: The agent which calculates the final outcome.
      :type agent: str
      :param other_agent: The other agent for which the final outcome is calculated.
      :type other_agent: str
      :param resource_id: The URI of the evaluated resource.
      :type resource_id: str
      :param logger: The logger object to be used by the agent.
      :type logger: BasicLogger
      :param discovery: Addresses of all agents within the scenario.
      :type discovery: dict
      :return: The final binary outcome.
      :rtype: tuple
      """

    # Predefined threshold values for comparison in travos. (may change)
    confidence_threshold = 0.95
    cooperation_threshold = 0.55

    # Calculate experience value. returns tuple
    experience_value = experience(agent, other_agent, logger)

    print(f"Experience tuple: {experience_value[1]}")
    print(f"Experience value: {experience_value[0]}")

    # Calculate confidence value
    confidence_value = calculate_confidence_value(experience_value)

    # Decision-making process (comparison)
    if confidence_value > confidence_threshold:
        print(
            f"Opinion not needed as confidence value '{confidence_value}' > confidence threshold "
            f" '{confidence_threshold}'")
        print(f"Experience value is Final trust score: {experience_value[0]}")

        final_trust_value = experience_value[0]

        if experience_value[0] > cooperation_threshold:
            print('Trustworthy')
            final_outcome = str((experience_value[1][0] + 1, experience_value[1][1]))
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, final_trust_value, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, final_outcome, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, None, resource_id)
            print(f"Past outcome: {experience_value[1]}")
            print(f"New outcome: {final_outcome}")
            print('-----*------')
        else:
            print('Not Trustworthy')
            final_outcome = str((experience_value[1][0], experience_value[1][1] + 1))
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, final_trust_value, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, final_outcome, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, None, resource_id)
            print(f"Past outcome: {experience_value[1]}")
            print(f"New outcome: {final_outcome}")
            print('-----*------')

    if confidence_value < confidence_threshold:

        # Calculate opinion value
        opinion_value = look_for_opinions(agent, other_agent, logger, discovery)

        final_trust_value = opinion_value

        print(
            f"Opinion needed as confidence value '{confidence_value}' < confidence threshold '{confidence_threshold}'")
        print(f"Opinion value is Final trust score: {opinion_value}")

        if opinion_value > cooperation_threshold and opinion_value >= experience_value[0]:
            print('Trustworthy')
            final_outcome = str((experience_value[1][0] + 1, experience_value[1][1]))
            trust_log_experience = str(experience_value[1])
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, experience_value[0], resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, trust_log_experience, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, final_trust_value, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, final_outcome, resource_id)
            print(f"Past outcome: {experience_value[1]}")
            print(f"New outcome: {final_outcome}")
            print('-----*------')
        else:
            print('Not Trustworthy')
            final_outcome = str((experience_value[1][0], experience_value[1][1] + 1))
            trust_log_experience = str(experience_value[1])
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, experience_value[0], resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.experience', other_agent, trust_log_experience, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, final_trust_value, resource_id)
            logger.write_to_agent_trust_log(agent, 'travos.opinion', other_agent, final_outcome, resource_id)
            print(f"Past outcome: {experience_value[1]}")
            print(f"New outcome: {final_outcome}")
            print('-----*------')

    return final_outcome
