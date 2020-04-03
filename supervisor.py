import argparse
import socket
from threading import Thread


class ScenarioRun(Thread):
    def __init__(self):
        Thread.__init__(self)
        pass


class Supervisor(Thread):
    def register_at_director(self):
        # TODO
        pass

    def run(self):
        self.register_at_director()
        # TODO open web socket
        # TODO handle incoming request

        # ip = '127.0.0.1'
        # buffer_size = 2048
        # tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # tcp_server.bind((ip, self.port))

    def __init__(self, max_agents, director_hostname="localhost"):
        Thread.__init__(self)
        self.director_hostname = director_hostname
        self.max_agents = max_agents


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--director", help="the hostname of the director, where the supervisor shall register at,"
                                                 "if not given supervisor expects to work at")
    parser.add_argument("max_agents", type=int,
                        help="the maximal number of agents existing in parallel under this supervisor")
    args = parser.parse_args()
    supervisor = Supervisor(args.max_agents, args.director) if args.director else Supervisor(args.max_agents)
    supervisor.start()


