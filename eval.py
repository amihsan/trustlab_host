import argparse
import aioprocessing
import importlib
import multiprocessing as multiproc
import re
from distutils.util import strtobool


class Evaluator:
    def run(self):
        self.pool.map(self.evaluate, self.args.files)

    def evaluate(self, file):
        print(file)

    def __init__(self, director_hostname, connector, logger_str, sec_conn=False):
        self.director_hostname = director_hostname
        self.logger_str = logger_str
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_pipe, self.pipe_dict["supervisor"] = aioprocessing.AioPipe(False)
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
