from trust.artifacts.content_trust.recommendation import recommendation as content_trust_recommendation
from trust.artifacts.content_trust.direct_experience import direct_experience as content_trust_direct_experience
from trust.artifacts.content_trust.popularity import popularity as content_trust_popularity
from trust.artifacts.content_trust.authority import authority as content_trust_authority
from trust.artifacts.content_trust.topic import topic as content_trust_topic
from trust.artifacts.content_trust.age import age_check as content_trust_age
from trust.artifacts.final_trust import weighted_avg_final_trust
from models import Scale, Observation
from loggers.basic_logger import BasicLogger


def eval_trust(agent, other_agent, observation, agent_behavior, scale, logger, discovery):
    """
    Calculate trust metrics and then finalize all values to one final trust value.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param observation: Content and metadata of message received and on which the trust is calculated.
    :type observation: Observation
    :param agent_behavior: Metrics to be used the agent.
    :type agent_behavior: dict
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The final trust value for one specific interaction between agent and the other agent.
    :rtype: float or int
    """
    trust_values = {}

    if 'content_trust.bias' in observation.details:
        bias_value = observation.details['content_trust.bias']
        logger.write_to_agent_trust_log(agent, "bias", other_agent, bias_value)
        trust_values['content_trust.bias'] = bias_value
    if 'content_trust.specificity' in observation.details:
        specificity_value = observation.details['content_trust.specificity']
        logger.write_to_agent_trust_log(agent, "specificity", other_agent, specificity_value)
        trust_values['content_trust.specificity'] = specificity_value
    if 'content_trust.likelihood' in observation.details:
        likelihood_value = observation.details['content_trust.likelihood']
        logger.write_to_agent_trust_log(agent, "likelihood", other_agent, likelihood_value)
        trust_values['content_trust.likelihood'] = likelihood_value
    if 'content_trust.incentive' in observation.details:
        incentive_value = observation.details['content_trust.incentive']
        logger.write_to_agent_trust_log(agent, "incentive", other_agent, incentive_value)
        trust_values['content_trust.incentive'] = incentive_value
    if 'content_trust.deception' in observation.details:
        deception_value = observation.details['content_trust.deception']
        logger.write_to_agent_trust_log(agent, "deception", other_agent, deception_value)
        trust_values['content_trust.deception'] = deception_value
    if 'content_trust.max_lifetime_seconds' in agent_behavior:
        age_punishment_value = content_trust_age(agent_behavior, observation, scale)
        logger.write_to_agent_trust_log(agent, "age", other_agent, age_punishment_value)
        if 'content_trust.enforce_lifetime' in agent_behavior and agent_behavior['content_trust.enforce_lifetime']:
            if age_punishment_value < scale.maximum_value():
                return scale.minimum_value()
        else:
            trust_values['content_trust_age'] = age_punishment_value
    if 'content_trust.direct_experience' in agent_behavior:
        direct_experience_value = content_trust_direct_experience(agent, other_agent, scale, logger)
        logger.write_to_agent_trust_log(agent, 'content_trust.direct_experience', other_agent, direct_experience_value)
        trust_values['content_trust.direct_experience'] = direct_experience_value
    if 'content_trust.authority' in agent_behavior:
        authority_value = content_trust_authority(agent_behavior['content_trust.authority'], other_agent, scale)
        logger.write_to_agent_trust_log(agent, 'content_trust.authority', other_agent, authority_value)
        trust_values['content_trust.authority'] = authority_value

    # old ----------------------------------
    if 'content_trust.popularity' in agent_behavior:
        popularity_value = content_trust_popularity(agent, other_agent, discovery, scale, logger)
        logger.write_to_agent_trust_log(agent, 'content_trust.popularity', other_agent, popularity_value)
        trust_values['content_trust.popularity'] = popularity_value
    if 'content_trust.recommendation' in agent_behavior:
        recommendation_value = content_trust_recommendation(agent, other_agent, scale, logger, discovery)
        logger.write_to_agent_trust_log(agent, 'content_trust.recommendation', other_agent, recommendation_value)
        trust_values['content_trust.recommendation'] = recommendation_value
    if 'content_trust.topic' in agent_behavior:
        topic_value = content_trust_topic(agent, other_agent, observation.topic, scale, logger)
        logger.write_to_agent_trust_log(agent, 'content_trust.topic', other_agent, topic_value)
        trust_values['content_trust.topic'] = topic_value
    # # old code from internship (do not use without refactoring)
    # if 'age' in agent_behavior:
    #     credibility_value = str(format(
    #         float(weights["age"]) * age_check(current_agent, other_agent, current_message[24:26]), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(bytes(get_current_time() + ', age trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    # if 'agreement' in agent_behavior:
    #     credibility_value = str(format(float(weights["agreement"]) * float(
    #         agreement(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(bytes(get_current_time() + ', agreement trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    # if 'provenance' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["provenance"]) * float(provenance(current_agent, current_message[16:18])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(bytes(get_current_time() + ', provenance trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    # if 'recency' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["recency"]) * float(recency(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(bytes(get_current_time() + ', recency trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    # if 'related resource' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["related resource"]) * float(related(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(bytes(get_current_time() + ', related resource trustvalue from: ', 'UTF-8') +
    #         bytes(other_agent, 'UTF-8') + bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    # if 'specificity' in agent_behavior:
    #     credibility_value = str(format(float(weights["specificity"]) * float(
    #         specificity(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', specificity trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') + bytes("\n", 'UTF-8'))
    #     fo.close()
    """
    final Trust calculations
    """
    # delete all metrics from final trust calculation, which results are set to None
    trust_values = {metric: value for metric, value in trust_values.items() if value is not None}
    final_trust_value = scale.default_value()
    if agent_behavior['__final__']:
        if agent_behavior['__final__']['name'] == 'weighted_average':
            final_trust_value = weighted_avg_final_trust(trust_values, agent_behavior['__final__']['weights'],
                                                         scale.default_value())
    return final_trust_value
