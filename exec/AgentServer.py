import socket
from threading import Thread
from trust_metrics import calc_trust_metrics
from artifacts.finalTrust import final_trust
from scenario_manager import Logging, get_current_time, ScenarioManager

untrustedAgents = []


class ClientThread(Thread):
    def run(self):
        try:
            msg = self.conn.recv(2048)
            reply = 'standard response'
            if msg != bytes('', 'UTF-8'):
                observation = msg.decode('utf-8')
                other_agent, current_agent, author, topic, message = observation.split(",", 4)

                # The incoming message is split and added to the logfiles
                agent_log_file_name = current_agent + ".txt"
                agent_log_path = Logging.LOG_PATH / agent_log_file_name
                agent_log = open(agent_log_path.absolute(), "ab+")
                write_string = get_current_time() + ", '" + current_agent + "' received from '" + other_agent + "' from author '" + author + "' with topic '" + topic + "' the message: " + message + '\n'
                agent_log.write(bytes(write_string, 'UTF-8'))
                agent_log.close()

                # Function call for the initialization of the trust values
                calc_trust_metrics(current_agent, other_agent, topic, ScenarioManager.SCENARIO)

                # Artifact finalTrust calculates the trust based on the saved values in the log file
                trust_value = final_trust(current_agent, other_agent)
                
                # Adding the trust value to the history file
                history_name = current_agent + "_history.txt"
                history_path = Logging.LOG_PATH / history_name
                history_file = open(history_path.absolute(), "ab+")
                history_file.write(bytes(get_current_time() + ', history trust value from: ' + other_agent + ' ' + str(trust_value) + '\n', 'UTF-8'))
                history_file.close()

                topic_name = current_agent + "_topic.txt"
                topic_path = Logging.LOG_PATH / topic_name
                with open(topic_path.absolute(), "ab+") as topic_file:
                    topic_file.write(bytes(
                        get_current_time() + ', topic trust value from: ' + other_agent + ' ' + topic + ' ' + str(trust_value) + '\n', 'UTF-8'))

                # Adding the trust value to the trust log
                trust_log_path = Logging.LOG_PATH / "trust_log.txt"
                trust_log = open(trust_log_path.absolute(), 'ab+')
                write_string = get_current_time() + ", agent '" + current_agent + "' trusts agent '" + other_agent + "' with value: " + str(trust_value) + '\n'
                trust_log.write(bytes(write_string, 'UTF-8'))
                trust_log.close()
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
            self.conn.send(bytes(str(reply), 'UTF-8'))
        except BrokenPipeError:
            pass
        return True

    def __init__(self, conn, id, port):
        Thread.__init__(self)
        self.conn = conn
        self.id = id
        self.port = port


class AgentServer(Thread):
    def run(self):
        buffer_size = 2048
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((self.ip_address, self.port))
        while True:
            tcp_server.listen(4)
            print("Agent '" + str(self.agent) + "' listens on " + str(self.ip_address) + ":" + str(self.port))
            (conn, (ip, port)) = tcp_server.accept()
            # TODO where is ID, an IP is added to ClientThread in original code
            new_thread = ClientThread(conn, self.agent, port)
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
            #         # TODO where is ID, an IP is added to ClientThread in original code
            #         new_thread = ClientThread(conn, self.id, port, self.scenario)
            #         new_thread.start()
            #         self.threads.append(new_thread)
            # tcp_server.close()

    def __init__(self, agent, ip_address, port):
        Thread.__init__(self)
        self.agent = agent
        self.ip_address = ip_address
        self.port = port
        self.threads = []


