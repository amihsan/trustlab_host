from artifacts.content_trust.recommendation import recommendation as content_trust_recommendation
from artifacts.content_trust.direct_experience import direct_experience as content_trust_direct_experience
from artifacts.content_trust.popularity import popularity as content_trust_popularity
from artifacts.content_trust.authority import authority as content_trust_authority
from artifacts.content_trust.topic import topic as content_trust_topic
from artifacts.final_trust import weighted_avg_final_trust


def eval_trust(agent, other_agent, current_topic, agent_behavior, trust_thresholds, logger, discovery):
    """
    calculate trust metrics
    """
    trust_values = {}
    if 'content_trust.direct_experience' in agent_behavior:
        direct_experience_value = content_trust_direct_experience(agent, other_agent, logger)
        logger.write_to_agent_trust_log(agent, "direct experience", other_agent, direct_experience_value)
        trust_values['content_trust.direct_experience'] = direct_experience_value
    if 'content_trust.authority' in agent_behavior and other_agent in agent_behavior['content_trust.authority']:
        authority_value = format(content_trust_authority(), '.2f')
        logger.write_to_agent_trust_log(agent, "authority", other_agent, authority_value)
        trust_values['content_trust.authority'] = authority_value
    if 'content_trust.popularity' in agent_behavior:
        popularity_value = content_trust_popularity(agent, other_agent, discovery, logger)
        logger.write_to_agent_trust_log(agent, "popularity", other_agent, popularity_value)
        trust_values['content_trust.popularity'] = popularity_value
    if 'content_trust.recommendation' in agent_behavior:
        recommendation_value = content_trust_recommendation(agent, other_agent, discovery, trust_thresholds['cooperation'], logger)
        logger.write_to_agent_trust_log(agent, "recommendation", other_agent, recommendation_value)
        trust_values['content_trust.recommendation'] = recommendation_value
    if 'content_trust.topic' in agent_behavior:
        topic_value = content_trust_topic(agent, other_agent, current_topic, logger)
        logger.write_to_agent_trust_log(agent, "topic", other_agent, topic_value)
        trust_values['content_trust.topic'] = topic_value
    # # old code from internship (do not use without refactoring
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
    final_trust_value = 0.0  # TODO: set to middle of given trust scale
    if agent_behavior['__final__']:
        if agent_behavior['__final__']['name'] == 'weighted_average':
            final_trust_value = weighted_avg_final_trust(trust_values, agent_behavior['__final__']['weights'])
    return final_trust_value


