agent = 'A1'
other_agent = 'A2'
service = 'Phone Call'
successful_interactions = int(input("No of successful interactions: "))
unsuccessful_interactions = int(input("No of unsuccessful interactions: "))
prev_history = (successful_interactions, unsuccessful_interactions)
confidence_threshold = 0.95
cooperation_threshold = 0.5
error_threshold = 0.2

# Opinion provider for agent A2 (static)
opinions = [{'A5': (15, 46)}, {'A6': (4, 1)}, {'A7': (3, 0)}]

# Static history
# prev_history = [{'A2': (17, 5)}, {'A3': (2, 15)}, {'A4': (18, 5)}]





