import argparse
import asyncio
import importlib
import re
import socket
from threading import Thread


class ScenarioRun(Thread):
    def __init__(self):
        Thread.__init__(self)
        pass


class Supervisor:
    def run(self):
        asyncio.run(self.connector.register_at_director(self.max_agents))

    def __init__(self, max_agents, director_hostname, connector):
        Thread.__init__(self)
        self.director_hostname = director_hostname
        self.max_agents = max_agents
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


