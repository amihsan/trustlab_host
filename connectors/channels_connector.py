import websockets
from connectors.basic_connector import BasicConnector
import json


class ChannelsConnector(BasicConnector):
    async def register_at_director(self, max_agents):
        uri = "ws://" + self.director_hostname + "/supervisors/"
        self.websocket = await websockets.client.connect(uri)
        register_max_agents = {"type": "max_agents", "max_agents": max_agents}
        await self.websocket.send(json.dumps(register_max_agents))
        response = await self.websocket.recv()
        print(response)

    def __init__(self, director_hostname):
        super().__init__(director_hostname)
        self.websocket = None



