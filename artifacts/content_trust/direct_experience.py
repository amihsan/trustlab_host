###############################################
# Direct Experience
# The tag values in the logfiles are combined to the Direct XP via the median


def direct_experience(agent, other_agent, scale,  logger):
    history_lines = logger.readlines_from_agent_history(agent)
    # getting all history values of the agent respective to the other agent
    history = [float(entry.split(" ")[-1]) for entry in history_lines if
               logger.line_about_other_agent(entry, other_agent)]
    # calculate direct experience
    direct_xp = sum(history) / len(history) if len(history) > 0 else scale.default_value()
    return direct_xp

