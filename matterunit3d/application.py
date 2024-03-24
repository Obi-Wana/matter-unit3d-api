import asyncio
import json
import aiohttp

from datetime import datetime, timedelta
from . import consts
from .unit3d import unit3d
from .matterbridge import matterbridge


class application:
    def __init__(self, unit3d_cfg, matterbridge_cfg):
        self.unit3d = unit3d(self, **unit3d_cfg)
        self.matterbridge = matterbridge(self, **matterbridge_cfg)
        self.services = [self.unit3d, self.matterbridge]
        self.running = False

    async def loop(self, service):
        while self.running:
            await service.watch()
            await asyncio.sleep(3)

    async def run(self):
        self.running = True
        async with aiohttp.ClientSession(headers = {"User-Agent": consts.user_agent}) as session:
            self.session = session
            await asyncio.wait(map(self.loop, self.services))
    
    def shutdown(self):
        self.running = False
    
    async def jsonlines(self, req):
        async for raw in req.content: # iterate over lines
            line = raw.decode()
            yield json.loads(line)

    def get_message_attributes(self, msg, source):
        if source == "matterbridgeapi":
            username = msg["username"]
            message = msg["text"]

            return username, message

        elif source == "unit3dchatbox":
            message_id = msg['id']
            username = msg["username"]
            message = msg["message"]
            created_at = datetime.strptime(msg['created_at'], '%Y-%m-%d %H:%M:%S')

            return message_id, username, message, created_at
