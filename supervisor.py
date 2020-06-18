import argparse
import importlib
import json
import re
import socket
import time
from contextlib import closing
from models import Scenario, Observation
from exec.AgentServer import AgentServer
from exec.AgentClient import AgentClient
import multiprocessing as multiproc
import aioprocessing


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
        # logging for all Agents their trust history and their topic values if given
        for agent in self.scenario.agents:
            self.logger.write_bulk_to_agent_history(agent, self.scenario.history[agent])
            if self.scenario.topics and agent in self.scenario.topics:
                self.logger.write_bulk_to_agent_topic_trust(agent, self.scenario.topics[agent])
        # creating servers
        for agent in self.agents_at_supervisor:
            free_port = self.find_free_port()
            local_discovery[agent] = self.ip_address + ":" + str(free_port)
            server = AgentServer(agent, self.ip_address, free_port, self.scenario.agents,
                                 self.scenario.metrics_per_agent[agent], self.scenario.weights,
                                 self.scenario.trust_thresholds, self.scenario.authorities, self.logger,
                                 self.observations_done)
            self.threads_server.append(server)
            server.start()
        discovery_message = {"type": "agent_discovery", "scenario_run_id": self.scenario_run_id,
                             "discovery": local_discovery}
        self.send_queue.put(discovery_message)
        self.discovery = self.receive_pipe.recv()["discovery"]
        print(self.discovery)

    def assert_scenario_start(self):
        start_confirmation = self.receive_pipe.recv()
        assert list(self.discovery.keys()) == self.scenario.agents  # all agents need to be discovered
        assert start_confirmation["scenario_status"] == "started"
        self.scenario_runs = True

    def run(self):
        self.prepare_scenario()
        self.assert_scenario_start()
        while self.scenario_runs:
            observation_dict = next((obs for obs in self.observations_to_exec if len(obs["before"]) == 0), None)
            if observation_dict is not None:
                observation = Observation(**observation_dict)
                ip, port = self.discovery[observation.receiver].split(":")
                client_thread = AgentClient(ip, port, json.dumps(observation_dict))
                # self.threads_client.append(client_thread)
                client_thread.start()
                self.observations_to_exec.remove(observation_dict)
            observation_done_dict = next((obs for obs in self.observations_done), None)
            if observation_done_dict is not None:
                done_message = {
                    "type": "observation_done",
                    "scenario_run_id": self.scenario_run_id,
                    "observation_id": observation_done_dict["observation_id"]
                }
                self.send_queue.put(done_message)
                self.remove_observation_dependency([observation_done_dict["observation_id"]])
                self.observations_done.remove(observation_done_dict)
                print(f"Exec after exec observation: {self.observations_to_exec}")
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'observation_done':
                    self.remove_observation_dependency(message["observations_done"])
                    print(f"Exec after done message: {self.observations_to_exec}")
        # for thread in self.threads_client:
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
        # for observation_dict in self.scenario.observations:
        #     # source, target, author, topic, message = observation.split(",", 4)
        #     observation = Observation(**observation_dict)
        #     ip, port = self.discovery[observation.receiver].split(":")
        #     client_thread = AgentClient(ip, port, json.dumps(observation_dict))
        #     # threads_client.append(client_thread)
        #     client_thread.start()
        #     time.sleep(1)

    def remove_observation_dependency(self, observations_done):
        for observation in self.observations_to_exec:
            observation["before"] = [obs_id for obs_id in observation["before"] if obs_id not in observations_done]

    def __init__(self, scenario_run_id, agents_at_supervisor, scenario, ip_address, send_queue, receive_pipe, logger,
                 observations_done):
        multiproc.Process.__init__(self)
        self.scenario_run_id = scenario_run_id
        self.agents_at_supervisor = agents_at_supervisor
        self.ip_address = ip_address
        self.send_queue = send_queue
        self.receive_pipe = receive_pipe
        self.discovery = {}
        self.threads_server = []
        self.threads_client = []
        self.scenario = scenario
        self.logger = logger
        self.scenario_runs = False
        self.observations_done = observations_done
        # filter observations that have to start at this supervisor
        self.observations_to_exec = [obs for obs in scenario.observations if obs["sender"] in agents_at_supervisor]
        

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
            # creating logger for new scenario run with already registered semaphore
            index_logger, logger_semaphore_dict = next((index, semaphore) for (index, semaphore) in
                                                       enumerate(self.logger_semaphores) if semaphore["used_by"] == "")
            logger_semaphore = logger_semaphore_dict["semaphore"]
            self.logger_semaphores[index_logger]["used_by"] = new_run["scenario_run_id"]
            module = importlib.import_module("loggers." + re.sub("([A-Z])", "_\g<1>", self.logger_str).lower()[1:])
            logger_class = getattr(module, self.logger_str)
            logger = logger_class(new_run["scenario_run_id"], logger_semaphore)
            # taking one observations_done list
            index_done, done_dict = next((index, obs_done_dict) for (index, obs_done_dict) in
                                         enumerate(self.observations_done) if obs_done_dict["used_by"] == "")
            observations_done = done_dict["list"]
            self.observations_done[index_done]["used_by"] = new_run["scenario_run_id"]
            # create and start scenario_run
            scenario_run = ScenarioRun(new_run["scenario_run_id"], new_run["agents_at_supervisor"],
                                       Scenario(**new_run["scenario"]), self.ip_address, self.send_queue, recv_end,
                                       logger, observations_done)
            self.scenario_runs.append(scenario_run)
            scenario_run.start()

    def __init__(self, ip_address, max_agents, director_hostname, connector, logger_str):
        self.ip_address = ip_address
        self.director_hostname = director_hostname
        self.max_agents = max_agents
        self.agents_in_use = 0
        self.takes_new_scenarios = True
        self.scenario_runs = []
        self.logger_str = logger_str
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_new_scenario, self.pipe_dict["new_run"] = aioprocessing.AioPipe(False)
        # setup logger semaphores for all possible scenario runs
        self.logger_semaphores = [{"semaphore": self.manager.Semaphore(1), "used_by": ""} for i in range(max_agents)]
        # setup observations_done lists
        self.observations_done = [{"list": self.manager.list(), "used_by": ""} for i in range(max_agents)]
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        connector_class = getattr(module, connector)
        self.connector = connector_class(director_hostname, max_agents, self.send_queue, self.pipe_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="The connector class to use for connecting to director.")
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="The hostname of the director, where the supervisor shall register at.")
    parser.add_argument("-ip", "--address", default="127.0.0.1",
                        help="The IP address of the supervisor itself.")
    parser.add_argument("-log", "--logger", default="FileLogger", choices=['FileLogger'],
                        help="The logger class to use for logging trust values during a scenario run.")
    parser.add_argument("max_agents", type=int,
                        help="The maximal number of agents existing in parallel under this supervisor.")
    args = parser.parse_args()
    # set multiprocessing start method
    multiproc.set_start_method('spawn')
    # init supervisor as class and execute
    supervisor = Supervisor(args.address, args.max_agents, args.director, args.connector, args.logger)
    supervisor.run()


