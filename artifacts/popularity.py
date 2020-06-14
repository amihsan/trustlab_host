###############################################
# Popularity check
# The popularity is calculated by averaging the recommendation

from artifacts.directxp import direct_experience


# TODO realize popularity via network requests
def popularity(agent, other_agent, agents, cooperation_threshold, logger):
    # other agent does ...
    # other_agent has to get all recommendations about itself
    agents_to_ask = [third_agent for third_agent in agents if third_agent != other_agent and direct_experience(other_agent, third_agent, logger) >= cooperation_threshold]
    recommendations = [direct_experience(other_agent, third_agent, logger) * direct_experience(third_agent, other_agent, logger) for third_agent in agents_to_ask]
    # all recommendations are weighted with direct experience and averaged
    popularity_value = sum(recommendations) / len(recommendations) if len(recommendations) > 0 else 0.00
    # ... other agent finished
    # popularity value of other agent has to be weighted with direct experience to other_agent
    popularity_value = direct_experience(agent, other_agent, logger) * popularity_value
    return popularity_value


