import argparse
import aioprocessing
import importlib
import multiprocessing as multiproc
import re
from distutils.util import strtobool


SCENARIO_NAMES = {
    'Basic Scenario': 3,
    'Basic Authority Scenario': 3,
    'Basic Topic Scenario': 3
}


class Evaluator:
    def run(self):
        self.connector.start()
        for scenario, raps in SCENARIO_NAMES.items():
            for i in range(0, raps):
                print(f"Starting scenario '{scenario}' run {i+1}...")
                run_message = {
                    'type': 'run_scenario',
                    'scenario': {'name': scenario},
                    'is_evaluator': True
                }
                self.send_queue.put(run_message)
                received_message = self.receive_pipe.recv()
                if received_message['type'] == 'scenario_run_id':
                    print(f"Got run id for '{scenario}' run {i+1}: {received_message['scenario_run_id']}")
                else:
                    raise RuntimeError(f"Did not receive scenario run ID after starting scenario '{scenario}' run {i+1}")
                received_message = self.receive_pipe.recv()
                if received_message['type'] == 'scenario_results':
                    print(f"Scenario '{scenario}' run {i+1} finished as '{received_message['scenario_run_id']}' "
                          f"executed under {received_message['supervisor_amount']} supervisors.\n\n")
        exit_message = {
            'type': 'end_socket'
        }
        self.send_queue.put(exit_message)

    def __init__(self, director_hostname, connector, logger_str, sec_conn=False):
        self.director_hostname = director_hostname
        self.logger_str = logger_str
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_pipe, self.pipe_dict["evaluator"] = aioprocessing.AioPipe(False)
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        connector_class = getattr(module, connector)
        self.connector = connector_class(director_hostname, 0, self.send_queue, self.pipe_dict, sec_conn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="The connector class to use for connecting to director.")
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="The hostname of the director, where the evaluation script shall register at.")
    parser.add_argument("-log", "--logger", default="FileLogger", choices=['FileLogger'],
                        help="The logger class to use for logging trust values during a scenario run.")
    parser.add_argument("-wss", "--sec-socket", type=lambda x: bool(strtobool(x)), nargs='?', const=True,
                        default=False, help="Whether to use a secure websocket connection to the director.")
    args = parser.parse_args()
    # set multiprocessing start method
    multiproc.set_start_method('spawn')
    # init supervisor as class and execute
    evaluator = Evaluator(args.director, args.connector, args.logger, args.sec_socket)
    evaluator.run()
