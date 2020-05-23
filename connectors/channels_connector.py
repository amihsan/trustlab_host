import websockets
from connectors.basic_connector import BasicConnector
import json


class ChannelsConnector(BasicConnector):
    async def register_at_director(self, max_agents):
        uri = "ws://" + self.director_hostname + "/supervisors/"
        self.websocket = await websockets.client.connect(uri)
        await self.set_max_agents(max_agents)

    async def set_max_agents(self, max_agents):
        register_max_agents = {"type": "max_agents", "max_agents": max_agents}
        await self.send_json(register_max_agents)
        response = await self.receive_json()
        print(response)

    async def get_next_run(self):
        return await self.receive_json()

    async def report_local_discovery(self, local_discovery):
        message = {"type": "scenario_discovery", "discovery": local_discovery}
        await self.send_json(message)
        return await self.receive_json()

    async def send_json(self, message):
        await self.websocket.send(json.dumps(message))

    async def receive_json(self):
        return await self.websocket.recv()

    def __init__(self, director_hostname):
        super().__init__(director_hostname)
        self.websocket = None



