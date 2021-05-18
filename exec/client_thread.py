import json
from threading import Thread

from trust_evaluation import eval_trust
from models import Observation
from artifacts.content_trust.recommendation import recommendation_response
from artifacts.content_trust.popularity import popularity_response


untrustedAgents = []


class ClientThread(Thread):
    def run(self):
        try:
            message = self.conn.recv(2048)
            if message != '':
                decoded_msg = message.decode('utf-8')
                if decoded_msg == "END":
                    self.conn.close()
                elif decoded_msg.startswith("aTLAS_trust_protocol::"):
                    trust_protocol_head, trust_protocol_message = decoded_msg.split("::")
                    trust_operation = trust_protocol_message.split("_")[0]
                    trust_value = 0.0
                    if trust_operation == "recommendation":
                        trust_value = recommendation_response(self.agent, trust_protocol_message.split("_")[1],
                                                              self.logger)
                    elif trust_operation == "popularity":
                        trust_value = popularity_response(self.agent, self.discovery,
                                                          self.trust_thresholds['cooperation'], self.logger)
                    trust_response = f"{trust_protocol_head}::{trust_protocol_message}::{trust_value}"
                    self.conn.send(bytes(trust_response, 'UTF-8'))
                else:
                    observation = Observation(**json.loads(decoded_msg))
                    self.logger.write_to_agent_message_log(observation)
                    trust_value = eval_trust(self.agent, observation.sender, observation.topic,
                                             self.agent_behavior, self.trust_thresholds, self.logger,
                                             self.discovery)
                    self.logger.write_to_agent_history(self.agent, observation.sender, trust_value)
                    self.logger.write_to_agent_topic_trust(self.agent, observation.sender, observation.topic, trust_value)
                    self.logger.write_to_trust_log(self.agent, observation.sender, trust_value)
                    # if float(trust_value) < self.scenario.trust_thresholds['lower_limit']:
                    #     untrustedAgents.append(other_agent)
                    #     print("+++" + current_agent + ", nodes beyond redemption: " + other_agent + "+++")
                    # if float(trust_value) > self.scenario.trust_thresholds['upper_limit'] or float(trust_value) > 1:
                    #     self.scenario.authority.append(current_agent[2:3])
                    # print("Node " + str(self.id) + " Server received data:", observation[2:-1])
                    self.conn.send(bytes('standard response', 'UTF-8'))
                    self.observations_done.append(observation.serialize())
        except BrokenPipeError:
            pass
        return True

    def __init__(self, conn, agent, agent_behavior, trust_thresholds, logger, observations_done, discovery):
        Thread.__init__(self)
        self.conn = conn
        self.agent = agent
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.trust_thresholds = trust_thresholds
        self.observations_done = observations_done
        self.discovery = discovery