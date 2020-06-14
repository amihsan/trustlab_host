###############################################
# Recommendations
from artifacts.directxp import direct_experience


# TODO realize recommendation via network requests
def recommendation(current_agent, other_agent, agents, cooperation_threshold, logger):
    agents_to_ask = [third_agent for third_agent in agents if third_agent != current_agent and third_agent != other_agent and direct_experience(current_agent, third_agent, logger) >= cooperation_threshold]
    recommendations = [direct_experience(current_agent, third_agent, logger) * direct_experience(third_agent, other_agent, logger) for third_agent in agents_to_ask]
    recommendation_value = sum(recommendations)/len(recommendations) if len(recommendations) > 0 else 0.00
    return recommendation_value


