from trust.artifacts.travos.experience import experience
from loggers.basic_logger import BasicLogger
from scipy.stats import beta
from scipy.integrate import quad


def calculate_confidence_value(experience_value):
    """
      Get confidence value  to determine the accuracy of direct experience trust value

      :param experience_value: Both Direct trust value and history tuple between agent and other agent.
      :type experience_value: tuple (trust value, (m, n))
      :return: Confidence value.
      :rtype: float or int
      """

    # Predefined value for travos. may change (such as 0.1)
    error_threshold = 0.2

    # Find out trust value and history tuple
    direct_trust = experience_value[0]
    direct_trust_tuple = experience_value[1]

    # Confidence value
    confidence_value = beta_integral(direct_trust - error_threshold, direct_trust + error_threshold,
                                     direct_trust_tuple[0] + 1, direct_trust_tuple[1] + 1) / \
                       beta_integral(0, 1, direct_trust_tuple[0] + 1, direct_trust_tuple[1] + 1)
    print(f"Confidence : {confidence_value}")
    return confidence_value


# integral function for travos confidence value calculation
def beta_integral(lower_limit, upper_limit, alpha, beta_):
    dist = beta(alpha, beta_)
    pdf = lambda x: dist.pdf(x)
    integral, _ = quad(pdf, lower_limit, upper_limit)
    return integral
