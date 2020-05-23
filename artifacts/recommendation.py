###############################################
# Recommendations
from artifacts.directxp import direct_experience


# TODO realize recommendation via network requests
def recommendation(current_agent, other_agent, agents, cooperation_threshold):
    agents_to_ask = [agent for agent in agents if agent != current_agent and agent != other_agent and direct_experience(current_agent, agent) >= cooperation_threshold]
    recommendations = [direct_experience(current_agent, agent) * direct_experience(agent, other_agent) for agent in agents_to_ask]
    recommendation_value = sum(recommendations)/len(recommendations) if len(recommendations) > 0 else 0.00
    return recommendation_value


