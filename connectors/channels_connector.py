import websockets
from connectors.basic_connector import BasicConnector


class ChannelsConnector(BasicConnector):
    async def register_at_director(self):
        uri = "ws://" + self.director_hostname + "/supervisors/"
        self.websocket = await websockets.client.connect(uri)
        await self.websocket.send("Hi")
        greeting = await self.websocket.recv()
        print(greeting)
        # ip = '127.0.0.1'
        # buffer_size = 2048
        # tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # tcp_server.bind((ip, self.port))

    def __init__(self, director_hostname):
        super().__init__(director_hostname)
        self.websocket = None



