import asyncio
import argparse
import importlib
import re
from threading import Thread
from asgiref.sync import async_to_sync


class ScenarioRun(Thread):
    def __init__(self):
        Thread.__init__(self)
        pass


class Supervisor:
    def run(self):
        asyncio.get_event_loop().run_until_complete(self.connector.register_at_director(self.max_agents))
        # async_to_sync(self.connector.register_at_director)(self.max_agents)
        print("test")
        while self.takes_new_scenarios:
            new_run = asyncio.get_event_loop().run_until_complete(self.connector.get_next_run())
            print(new_run)

    def __init__(self, max_agents, director_hostname, connector):
        self.director_hostname = director_hostname
        self.max_agents = max_agents
        self.agents_in_use = 0
        self.takes_new_scenarios = True
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        class_ = getattr(module, connector)
        self.connector = class_(director_hostname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="the hostname of the director, where the supervisor shall register at.")
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="the connector class to use for connecting to director.")
    parser.add_argument("max_agents", type=int,
                        help="the maximal number of agents existing in parallel under this supervisor")
    args = parser.parse_args()
    supervisor = Supervisor(args.max_agents, args.director, args.connector)
    supervisor.run()


