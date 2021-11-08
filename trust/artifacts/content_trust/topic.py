from models import Scale


def topic(current_topics, trusted_topics, scale):
    """
    Calculate topic trust by reading the relevant topics for the current resource and comparing them to the set of
    topics that the resource is trusted on. The returned topic trust value expresses the congruency of both sets,
    normalized to the given scale.

    :param current_topics: The topics of the message received and on which the trust is calculated.
    :type current_topics: list
    :param trusted_topics: The topics that the resource is trusted on.
    :type trusted_topics: list
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: The topic trust value.
    :rtype: float or int
    """

    if len(current_topics) == 0:
        return scale.default_value()

    count_congruent = len(set(current_topics) & set(trusted_topics))
    score = count_congruent / len(current_topics)
    return scale.normalize_value_to_scale(score, 0, 1)
