import json
import posixpath
import traceback
import uuid

from datetime import datetime, timedelta
from .service import service


class unit3d(service):
    def init(self, username, fmt = "{username}: {message}"):
        self.username = username
        self.fmt = fmt
    
    def request(self, method, url):
        url = self.addr + url + self.chatroom_id + "?api_token=" + self.token

        return self.app.session.request(method, url)

    def post(self, url, msg):
        username, message = self.app.get_message_attributes(msg, "matterbridgeapi")
        message = (f'[{username}] {message}')

        payload = {
            'username': self.chatroom_id,
            'message': message,
            'chatroom_id': int(self.chatroom_id),
            'save': 'true',
            'targeted': '0',
            'user_id': '2'
        }

        url = self.addr + url
        return self.app.session.post(url, json = payload)

    async def send(self, msg):
        async with self.post("/api/chats/messages?api_token=" + self.token, msg) as req:
            if req.status >= 400:
                self.logger.error(f"{req.status}\n{await req.text()}")
