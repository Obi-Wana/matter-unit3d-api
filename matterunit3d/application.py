import asyncio
import json
import aiohttp

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
            await asyncio.sleep(2)

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
            if line.strip() == "|": # placed between objects by Discourse
                continue
            yield json.loads(line)
