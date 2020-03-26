from datetime import *
from trustlab.lab.artifacts.recommendation import recommendation
from trustlab.lab.artifacts.directxp import direct_experience
from trustlab.lab.artifacts.popularity import popularity
from trustlab.lab.artifacts.authority import authority
from trustlab.lab.artifacts.agreement import agreement
from trustlab.lab.artifacts.age import age_check
from trustlab.lab.artifacts.recency import recency
from trustlab.lab.artifacts.relatedRecources import related
from trustlab.lab.artifacts.specificity import specifi
from trustlab.lab.artifacts.provenance import provenance
from trustlab.lab.artifacts.topic import topic
from trustlab.lab.config import Logging, get_current_time

############################################################################
# ---The trust_initialization function starts with the imported behavior models
# ---and checks them for behavior-keywords. Those keywords trigger the specific
# ---function call to calculate the corresponding value from the artifacts.
# ---This is needed to calculate the final trust value


def calc_trust_metrics(current_agent, other_agent, current_topic, scenario):
    file_name = current_agent + "_trust_log.txt"
    log_path = Logging.LOG_PATH / file_name
    agent_behavior = scenario.metrics_per_agent[current_agent]

    #################################################
    # Artifact Calculation

    if 'direct experience' in agent_behavior:
        direct_experience_value = format(scenario.weights["direct experience"] * direct_experience(current_agent, other_agent), '.2f')
        fo = open(log_path.absolute(), "ab+")
        fo.write(
            bytes(get_current_time() + ', direct experience trust value from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
            bytes(' ' + direct_experience_value, 'UTF-8') +
            bytes("\n", 'UTF-8'))
        fo.close()
        
    if 'authority' in agent_behavior and other_agent in scenario.authorities[current_agent]:
        authority_value = format(scenario.weights["authority"] * authority(), '.2f')
        fo = open(log_path.absolute(), "ab+")
        fo.write(
            bytes(get_current_time() + ', authority trust value from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
            bytes(' ' + authority_value, 'UTF-8') +
            bytes("\n", 'UTF-8'))
        fo.close()
        pass

    if 'popularity' in agent_behavior:
        popularity_value = format(float(scenario.weights["popularity"]) * float(popularity(current_agent, other_agent, scenario.agents, scenario.trust_thresholds['cooperation'])), '.2f')
        fo = open(log_path.absolute(), "ab+")
        fo.write(
            bytes(get_current_time() + ', popularity trust value from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
            bytes(' ' + popularity_value, 'UTF-8') +
            bytes("\n", 'UTF-8'))
        fo.close()

    if 'recommendation' in agent_behavior:
        recommendation_value = format(scenario.weights["recommendation"] * recommendation(current_agent, other_agent, scenario.agents, scenario.trust_thresholds['cooperation']), '.2f')
        fo = open(log_path.absolute(), "ab+")
        fo.write(
            bytes(get_current_time() + ', recommendation trust value from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
            bytes(' ' + recommendation_value, 'UTF-8') +
            bytes("\n", 'UTF-8'))
        fo.close()

    if 'topic' in agent_behavior:
        topic_value = format(scenario.weights["topic"] * topic(current_agent, other_agent, current_topic), '.2f')
        fo = open(log_path.absolute(), "ab+")
        fo.write(
            bytes(get_current_time() + ', topic trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
            bytes(' ' + topic_value, 'UTF-8') +
            bytes("\n", 'UTF-8'))
        fo.close()

    # if 'age' in agent_behavior:
    #     credibility_value = str(format(
    #         float(scenario.weights["age"]) * age_check(current_agent, other_agent, current_message[24:26]),
    #         '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', age trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'agreement' in agent_behavior:
    #     credibility_value = str(format(float(scenario.weights["agreement"]) * float(
    #         agreement(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', agreement trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'provenance' in agent_behavior:
    #     credibility_value = str(
    #         format(float(scenario.weights["provenance"]) * float(provenance(current_agent, current_message[16:18])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', provenance trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'recency' in agent_behavior:
    #     credibility_value = str(
    #         format(float(scenario.weights["recency"]) * float(recency(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', recency trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'related resource' in agent_behavior:
    #     credibility_value = str(
    #         format(float(scenario.weights["related resource"]) * float(related(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', related resource trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'specificity' in agent_behavior:
    #     credibility_value = str(format(float(scenario.weights["specificity"]) * float(
    #         specifi(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', specificity trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()




