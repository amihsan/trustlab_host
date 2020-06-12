

class ScenarioManager:
    SCENARIO = None
    SHUTDOWN = False

    @staticmethod
    def set_scenario(scenario):
        ScenarioManager.SCENARIO = scenario

    @staticmethod
    def shutdown_server():
        ScenarioManager.SHUTDOWN = True




