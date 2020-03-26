###############################################
# Popularity check
# The popularity is calculated by averaging the recommendation

from trustlab.lab.artifacts.directxp import direct_experience


# TODO realize popularity via network requests
def popularity(current_agent, other_agent, agents, cooperation_threshold):
    # other agent does ...
    # other_agent has to get all recommendations about itself
    agents_to_ask = [agent for agent in agents if agent != other_agent and direct_experience(other_agent, agent) >= cooperation_threshold]
    recommendations = [direct_experience(other_agent, agent) * direct_experience(agent, other_agent) for agent in agents_to_ask]
    # all recommendations are weighted with direct experience and averaged
    popularity_value = sum(recommendations) / len(recommendations) if len(recommendations) > 0 else 0.00
    # ... other agent finished
    # popularity value of other agent has to be weighted with direct experience to other_agent
    popularity_value = direct_experience(current_agent, other_agent) * popularity_value
    return popularity_value


