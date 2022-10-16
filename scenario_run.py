import json
import socket
import time
from contextlib import closing
import multiprocessing as multiproc

from models import Observation
from exec.agent_server import AgentServer
from exec.agent_client import AgentClient
import resource
from config import METRICS_ON_INIT


class ScenarioRun(multiproc.Process):
    """
    The supervisors subprocess proxy for each scenario run to be executed with at least one agent at the supervisor.
    """
    @staticmethod
    def find_free_port():
        """
        Find a free TCP port to use for a new socket.
        Method copied from https://stackoverflow.com/a/45690594

        :return: Free port number.
        """
        resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def prepare_scenario(self, all_agents):
        """
        Prepare the scenario run by `1)` logging for all agents their initial trust value logs,
        `2)` initializing all local agents' server(s), `3)` sending the local discovery to the director,
        and `4)` receiving and saving the global discovery with all agents' addresses.
        """
        local_discovery = {}
        # logging for all Agents their trust history values if given
        #for agent in self.scenario.agents:
        i = 0
        print("Analyze History for all Agents")
        for agent in self.agents_at_supervisor:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Analyze History for: " + str(agent) + " [" + current_time + "]" + " [" + str(i) + "]")
            history = self.communicationHelper.get_agent_history(agent)
            self.logger.write_bulk_to_agent_history(agent, history['data'])
            # topic no longer part of agent, but part of resource
            #if self.scenario.agent_uses_metric(agent, 'content_trust.topic'):
            #    self.logger.write_bulk_to_agent_topic_trust(agent, self.scenario.agents_with_metric(
            #        'content_trust.topic')[agent])
            i+=1
        # creating servers
        i = 0
        print("Analyze Scales for all Agents")
        for agent in self.agents_at_supervisor:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Analyze  Scales for: " + str(agent) + " [" + current_time + "]" + " [" + str(i) + "]")
            free_port = self.find_free_port()
            local_discovery[agent] = self.ip_address + ":" + str(free_port)
            metrics = None
            if METRICS_ON_INIT:
                metrics = self.communicationHelper.get_agent_metrics(agent)
            scales = self.communicationHelper.get_agent_scales(agent)
            server = AgentServer(agent, self.ip_address, free_port, metrics,
                                 scales['data'], self.logger, self.observations_done)
            self.threads_server.append(server)
            server.start()
            i+=1
        discovery_message = {"type": "agent_discovery", "scenario_run_id": self.scenario_run_id,
                             "discovery": local_discovery}
        print("Send Discovery")
        print(time.time())
        self.send_queue.put(discovery_message)
        print("Send Discovery Done")
        print(time.time())
        message = self.receive_pipe.recv()
        print("Discovery message Reseived")
        print(time.time())
        self.discovery = message["discovery"]
        for thread in self.threads_server:
            thread.set_discovery(self.discovery)
        print("End Preparation")
        print(time.time())

    def assert_scenario_start(self, agents):
        """
        Wait for the scenario run to start by receiving the respective message from the director.
        It further asserts that all scenario's agents have to be discovered before the start and
        thus throws an AssertionError if not.

        :rtype: None
        :raises AssertionError: Not all agents are discovered or the received message is not the start signal.
        """
        assert list(self.discovery.keys()) == agents  # all agents need to be discovered
        self.scenario_runs = True

    def run(self):
        """
        Executes the scenario run by first preparing the scenario and then awaiting the scenario to start.
        During scenario run, Supervisor is within this run method scheduling the observations by starting
        local observations if all observations before were already executed. Further, it resolves the before
        dependencies of still existing observations to be executed by an agent under this supervisor if receiving
        an observation_done message. It sends out an observation_done message itself if one observation was executed
        by one agent under this supervisor.

        :rtype: None
        """

        all_agents = []
        for agentdefinition in self.communicationHelper.get_all_agents():
           all_agents.append(agentdefinition['name'])

        self.prepare_scenario(all_agents)
        self.assert_scenario_start(all_agents)
        observation_dict = None
        while self.scenario_runs:
            for server in self.threads_server:
                if server.get_agent_behavior():
                    self.communicationHelper.send_get_agent_metrics(server.agent)

            if observation_dict is not None:
                observation = Observation(**observation_dict)
                ip, port = self.discovery[observation.receiver].split(":")
                print(f"Sending observation {observation.observation_id} to {ip}:{port}")
                client_thread = AgentClient(ip, int(port), json.dumps(observation_dict))
                self.threads_client.append(client_thread)
                client_thread.start()
                done_message = {
                    "type": "agent_free",
                    "scenario_run_id": self.scenario_run_id,
                    "scenario_name": self.scenario_name,
                    "agent": observation.sender
                }
                self.send_queue.put(done_message)
                observation_dict = None
            observation_done_dict = next((obs for obs in self.observations_done), None)
            if observation_done_dict is not None:
                done_message = {
                    "type": "observation_done",
                    "scenario_run_id": self.scenario_run_id,
                    "scenario_name": self.scenario_name,
                    "observation_id": observation_done_dict["observation_id"],
                    "receiver": observation_done_dict["receiver"],
                    "trust_log": '<br>'.join(self.logger.read_lines_from_trust_log_str()),
                    "trust_log_dict": self.logger.read_lines_from_trust_log(),
                    "receiver_trust_log": '<br>'.join(self.logger.read_lines_from_agent_trust_log_str(
                        observation_done_dict["receiver"])),
                    "receiver_trust_log_dict": self.logger.read_lines_from_agent_trust_log(
                        observation_done_dict["receiver"]),
                }
                self.send_queue.put(done_message)
                self.observations_done.remove(observation_done_dict)
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'scenario_end':
                    for thread in self.threads_client:
                        if thread.is_alive():
                            thread.join()
                    for thread in self.threads_server:
                        thread.end_server()
                        if thread.is_alive():
                            thread.join()
                    self.scenario_runs = False
                if message['type'] == 'new_observation' and message['data']['sender'] in self.agents_at_supervisor:
                    observation_dict = message['data']
                    print("Agent: " + str(observation_dict['sender']) + " got new observation: " + str(observation_dict['observation_id']))
                if message['type'] == 'get_metrics_per_agent' and message['agent'] in self.agents_at_supervisor:
                    agent = message['agent']
                    for server in self.threads_server:
                        if server.agent == agent:
                            server.set_agent_behavior(message['data'])
                    del message['data']

        end_message = {
            'type': 'scenario_end',
            'scenario_run_id': self.scenario_run_id
        }
        self.supervisor_pipe.send(end_message)

    def remove_observation_dependency(self, observations_done):
        """
        Removes any observations given from all `observations_to_exec`'s `before` dependencies.

        :param observations_done: All observation ids to be removed from the `before` dependency.
        :type observations_done: list
        :rtype: None
        """
        for observation in self.observations_to_exec:
            observation["before"] = [obs_id for obs_id in observation["before"] if obs_id not in observations_done]

    def __init__(self, scenario_run_id, scenario_name, agents_at_supervisor, ip_address, send_queue, receive_pipe, logger,
                 observations_done, supervisor_pipe):
        multiproc.Process.__init__(self)
        self.scenario_run_id = scenario_run_id
        self.scenario_name = scenario_name
        self.agents_at_supervisor = agents_at_supervisor
        self.ip_address = ip_address
        self.send_queue = send_queue
        self.receive_pipe = receive_pipe
        self.discovery = {}
        self.threads_server = []
        self.threads_client = []
        self.logger = logger
        self.scenario_runs = False
        self.observations_done = observations_done
        self.supervisor_pipe = supervisor_pipe
        self.communicationHelper = CommunicationHelper(scenario_run_id, scenario_name, send_queue, receive_pipe)
class CommunicationHelper:

    def __init__(self, scenario_run_id, scenario_name, send_queue, receive_pipe):
        self.send_queue = send_queue
        self.receive_pipe = receive_pipe
        self.scenario_run_id = scenario_run_id
        self.scenario_name = scenario_name

    def get_all_agents(self):
        request = True
        requestmessage = {
            "type": "get_all_agents",
            "scenario_run_id": self.scenario_run_id,
            "scenario_name": self.scenario_name
        }
        self.send_queue.put(requestmessage)

        while request:
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'get_all_agents':
                    return message['data']

    def get_agent_metrics(self, agent):
        request = True
        requestmessage = {
            "type": "get_metrics_per_agent",
            "scenario_run_id": self.scenario_run_id,
            "scenario_name": self.scenario_name,
            "agent": agent
        }
        self.send_queue.put(requestmessage)

        while request:
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'get_metrics_per_agent' and message['agent'] == agent:
                    return message

    def send_get_agent_metrics(self, agent):
        requestmessage = {
            "type": "get_metrics_per_agent",
            "scenario_run_id": self.scenario_run_id,
            "scenario_name": self.scenario_name,
            "agent": agent
        }
        self.send_queue.put(requestmessage)

    def get_agent_scales(self, agent):
        request = True
        requestmessage = {
            "type": "get_scales_per_agent",
            "scenario_name": self.scenario_name,
            "scenario_run_id": self.scenario_run_id,
            "agent": agent
        }
        self.send_queue.put(requestmessage)

        while request:
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'get_scales_per_agent' and message['agent'] == agent:
                    return message

    def get_agent_history(self, agent):
        request = True
        requestmessage = {
            "type": "get_history_per_agent",
            "scenario_name": self.scenario_name,
            "scenario_run_id": self.scenario_run_id,
            "agent": agent
        }
        self.send_queue.put(requestmessage)

        while request:
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'get_history_per_agent' and message['agent'] == agent:
                    return message