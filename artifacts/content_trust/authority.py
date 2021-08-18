

def authority(scale):
    """
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: Returns the boost for authorities.
    :rtype: float or int
    """
    return scale.maximum_value()
