from scipy.stats import beta
from scipy.integrate import quad
from scenario import agent, other_agent, service, prev_history, error_threshold


# Calculate experience value from past interaction history
def experience(agent, other_agent, service):

    m = prev_history[0] + 1
    n = prev_history[1] + 1
    direct_xp = m / (m + n)
    print(f"{agent} trusts {other_agent} for {service} service with trust value: {direct_xp}")
    return direct_xp


# Store experience value
experience_value = experience(agent, other_agent, service)


# print(experience_value)

# Confidence value calculate using Beta Probability Density Function
def beta_integral(lower_limit, upper_limit, alpha, beta_):
    dist = beta(alpha, beta_)
    pdf = lambda x: dist.pdf(x)
    integral, _ = quad(pdf, lower_limit, upper_limit)
    return integral


# Beta distribution limit
lower_limit = experience_value - error_threshold
# print(lower_limit)
upper_limit = experience_value + error_threshold
# print(upper_limit)

# Shape parameter for beta distribution3
alpha = prev_history[0] + 1
beta_ = prev_history[1] + 1

# Store confidence value
confidence_value = beta_integral(lower_limit, upper_limit, alpha, beta_) / beta_integral(0, 1, alpha, beta_)
print(f"Experience value: {experience_value} and Confidence value: {confidence_value}")
