###############################################
# Recommendations
from artifacts.content_trust.direct_experience import direct_experience
from exec.ask_others import ask_other_agent


def recommendation(current_agent, other_agent, discovery, scale, logger):
    agents_to_ask = [third_agent for third_agent in discovery if third_agent != current_agent and
                     third_agent != other_agent and
                     direct_experience(current_agent, third_agent, scale, logger) >= scale.minimum_to_trust_others()]
    recommendations = ask_for_recommendations(current_agent, other_agent, agents_to_ask, scale, discovery, logger)
    default = scale.default_value()
    recommendation_value = sum(recommendations)/len(recommendations) if len(recommendations) > 0 else default
    return recommendation_value


def ask_for_recommendations(current_agent, other_agent, agents_to_ask, scale, discovery, logger):
    recommendations = []
    message = f"recommendation_{other_agent}"
    for third_agent in agents_to_ask:
        remote_ip, remote_port = discovery[third_agent].split(":")
        received_value = ask_other_agent(remote_ip, int(remote_port), message)
        recommendations.append(direct_experience(current_agent, third_agent, scale, logger) * received_value)
    return recommendations


def recommendation_response(agent, recommendation_agent, scale, logger):
    return direct_experience(agent, recommendation_agent, scale, logger)

