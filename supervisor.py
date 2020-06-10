import asyncio
import argparse
import importlib
import json
import re
import socket
from contextlib import closing
from models import Scenario
from exec.AgentServer import AgentServer
import multiprocessing as multiproc
import aioprocessing
from asgiref.sync import async_to_sync


class ScenarioRun(multiproc.Process):
    # method copied from https://stackoverflow.com/a/45690594
    @staticmethod
    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def prepare_scenario(self):
        local_discovery = {}
        # creating servers
        for agent in self.agents_at_supervisor:
            free_port = self.find_free_port()
            local_discovery[agent] = self.ip_address + ":" + str(free_port)
            server = AgentServer(agent, self.ip_address, free_port)
            self.threads_server.append(server)
            server.start()
        discovery_message = {"type": "agent_discovery", "scenario_run_id": self.scenario_run_id,
                             "discovery": local_discovery}
        self.send_queue.put(discovery_message)
        self.discovery = self.receive_pipe.recv()["discovery"]
        print(self.discovery)

    def assert_scenario_start(self):
        start_confirmation = self.receive_pipe.recv()
        assert self.discovery.keys() == self.scenario["agents"]
        assert start_confirmation["scenario_status"] == "started"

    def run(self):
        self.prepare_scenario()
        self.assert_scenario_start()
        pass
        # ServerStatus.set_scenario(scenario)
        #
        # # logging for all Agents their trust history and their topic values if given
        # for agent in scenario.agents:
        #     history_name = agent + "_history.txt"
        #     history_path = Logging.LOG_PATH / history_name
        #     with open(history_path.absolute(), "ab+") as history_file:
        #         for other_agent, history_value in scenario.history[agent].items():
        #             history_file.write(bytes(get_current_time() + ', history trust value from: ' + other_agent + ' ' +
        #                                      str(history_value) + '\n', 'UTF-8'))
        #     topic_name = agent + "_topic.txt"
        #     topic_path = Logging.LOG_PATH / topic_name
        #     with open(topic_path.absolute(), "ab+") as topic_file:
        #         if scenario.topics and agent in scenario.topics:
        #             for other_agent, topic_dict in scenario.topics[agent].items():
        #                 if topic_dict:
        #                     for topic, topic_value in topic_dict.items():
        #                         # TODO topic not always required to be single word
        #                         topic_file.write(bytes(get_current_time() + ', topic trust value from: ' + other_agent + ' ' + topic + ' ' + str(topic_value) + '\n', 'UTF-8'))
        # for observation in scenario.observations:
        #     source, target, author, topic, message = observation.split(",", 4)
        #     port = 2000 + scenario.agents.index(target)
        #     client_thread = AgentClient(source, self.HOST, port, observation)
        #     threads_client.append(client_thread)
        #     client_thread.start()
        #     file_path = Logging.LOG_PATH / "director_log.txt"
        #     director_file = open(file_path.absolute(), "ab+")
        #     # write_string = get_current_time() + ", '" + source + "' sends '" + target + "' from author '" + author + "' with topic '" + topic + "' the message: " + message + '\n'
        #     write_string = get_current_time() + ", '" + source + "' sends '" + target + "', topic '" + topic + "', message: " + message + '\n'
        #     director_file.write(bytes(write_string, 'UTF-8'))
        #     director_file.close()
        #     time.sleep(1)
        # for thread in threads_client:
        #     thread.join()
        # for server in thread_server:
        #     for thread in server.threads:
        #         thread.join()
        # # ServerStatus.shutdown_server()
        # # for server in thread_server:
        # #     server.join()
        # # while len(threads_client) > 0 or any([len(server.threads) > 0 for server in thread_server]):
        # #     threads_client = [thread for thread in threads_client if thread.is_alive()]
        # return Logging.LOG_PATH / "director_log.txt", Logging.LOG_PATH / "trust_log.txt"

    def __init__(self, scenario_run_id, agents_at_supervisor, scenario, ip_address, send_queue, receive_pipe):
        multiproc.Process.__init__(self)
        self.scenario_run_id = scenario_run_id
        self.agents_at_supervisor = agents_at_supervisor
        self.scenario = scenario
        self.ip_address = ip_address
        self.send_queue = send_queue
        self.receive_pipe = receive_pipe
        self.discovery = {}
        self.threads_server = []
        self.threads_client = []


class Supervisor:
    def run(self):
        self.connector.start()
        # async_to_sync(self.connector.register_at_director)(self.max_agents)
        while self.takes_new_scenarios:
            new_run = self.receive_new_scenario.recv()
            # TODO check if enough agents are left and scenario can be really started
            self.agents_in_use += len(new_run["agents_at_supervisor"])
            recv_end, send_end = aioprocessing.AioPipe(False)
            self.pipe_dict[new_run["scenario_run_id"]] = send_end
            scenario_run = ScenarioRun(new_run["scenario_run_id"], new_run["agents_at_supervisor"],
                                       Scenario(**new_run["scenario"]), self.ip_address, self.send_queue, recv_end)
            self.scenario_runs.append(scenario_run)
            scenario_run.start()

    def __init__(self, ip_address, max_agents, director_hostname, connector):
        self.ip_address = ip_address
        self.director_hostname = director_hostname
        self.max_agents = max_agents
        self.agents_in_use = 0
        self.takes_new_scenarios = True
        self.scenario_runs = []
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_new_scenario, self.pipe_dict["new_run"] = aioprocessing.AioPipe(False)
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        class_ = getattr(module, connector)
        self.connector = class_(director_hostname, max_agents, self.send_queue, self.pipe_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="The connector class to use for connecting to director.")
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="The hostname of the director, where the supervisor shall register at.")
    parser.add_argument("-ip", "--address", default="127.0.0.1",
                        help="The IP address of the supervisor itself.")
    parser.add_argument("max_agents", type=int,
                        help="The maximal number of agents existing in parallel under this supervisor.")
    args = parser.parse_args()
    # set multiprocessing start method
    multiproc.set_start_method('spawn')
    # init supervisor as class and execute
    supervisor = Supervisor(args.address, args.max_agents, args.director, args.connector)
    supervisor.run()


