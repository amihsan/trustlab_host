import json
import socket
from threading import Thread
from trust_metrics import calc_trust_metrics
from artifacts.finalTrust import final_trust
from scenario_manager import ScenarioManager
from models import Observation

untrustedAgents = []


class ClientThread(Thread):
    def run(self):
        try:
            message = self.conn.recv(2048)
            if message != '':
                observation_str = message.decode('utf-8')
                observation = Observation(**json.loads(observation_str))
                self.logger.write_to_agent_message_log(observation)
                calc_trust_metrics(self.agent, observation.sender, observation.topic, self.agents,
                                   self.agent_behavior, self.weights, self.trust_thresholds, self.authorities,
                                   self.logger)
                trust_value = final_trust(self.agent, observation.sender, self.logger)
                self.logger.write_to_agent_history(self.agent, observation.sender, trust_value)
                self.logger.write_to_agent_topic_trust(self.agent, observation.sender, observation.topic, trust_value)
                self.logger.write_to_trust_log(self.agent, observation.sender, trust_value)
                # print("_______________________________________")
                # # print("_____________________" + trust_value + "-__________")
                #
                # if float(trust_value) < self.scenario.trust_thresholds['lower_limit']:
                #     untrustedAgents.append(other_agent)
                #     print("+++" + current_agent + ", nodes beyond redemption: " + other_agent + "+++")
                # if float(trust_value) > self.scenario.trust_thresholds['upper_limit'] or float(trust_value) > 1:
                #     self.scenario.authority.append(current_agent[2:3])
                # print("Node " + str(self.id) + " Server received data:", observation[2:-1])
                # print("_______________________________________")
            self.conn.send(bytes('standard response', 'UTF-8'))
        except BrokenPipeError:
            pass
        return True

    def __init__(self, conn, agent, agents, agent_behavior, weights, trust_thresholds, authorities, logger):
        Thread.__init__(self)
        self.conn = conn
        self.agent = agent
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.weights = weights
        self.trust_thresholds = trust_thresholds
        self.authorities = authorities
        self.agents = agents


class AgentServer(Thread):
    def run(self):
        buffer_size = 2048
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((self.ip_address, self.port))
        while True:
            tcp_server.listen(4)
            print(f"Agent '{self.agent}' listens on {self.ip_address}:{self.port}")
            (conn, (ip, port)) = tcp_server.accept()
            new_thread = ClientThread(conn, self.agent, self.agents, self.agent_behavior, self.weights,
                                      self.trust_thresholds, self.authorities, self.logger)
            new_thread.start()
            self.threads.append(new_thread)
            # self.threads = [thread for thread in self.threads if thread.is_alive()]
            # while not ServerStatus.SHUTDOWN:
            #     try:
            #         tcp_server.settimeout(1)
            #         tcp_server.listen(4)
            #         (conn, (ip, port)) = tcp_server.accept()
            #     except socket.timeout:
            #         pass
            #     else:
            #         new_thread = ClientThread(conn, self.id, port, self.scenario)
            #         new_thread.start()
            #         self.threads.append(new_thread)
            # tcp_server.close()

    def __init__(self, agent, ip_address, port, agents, agent_behavior, weights, trust_thresholds, authorities, logger):
        Thread.__init__(self)
        self.agent = agent
        self.ip_address = ip_address
        self.port = port
        self.threads = []
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.weights = weights
        self.trust_thresholds = trust_thresholds
        self.authorities = authorities
        self.agents = agents

