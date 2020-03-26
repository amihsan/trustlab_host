import socket
from threading import Thread


class AgentClient(Thread):
    def run(self):
        buffer_size = 2000
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect(('127.0.0.1', self.port))
        # send message
        tcp_client.send(bytes(self.msg, 'UTF-8'))
        receive_data = tcp_client.recv(buffer_size)
        # print("data sent at :"  + time.ctime(time.time()))
        receive_data = receive_data.decode()
        print(receive_data)
        tcp_client.close()
        return True

    def __init__(self, ID, host, port, msg):
        Thread.__init__(self)
        self.ID = ID
        self.host = host
        self.port = port
        self.msg = msg




