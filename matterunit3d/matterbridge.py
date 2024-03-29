from .service import service


class matterbridge(service):
    def request(self, method, url, *args, headers = None, **kwargs):
        if headers is None:
            headers = {}
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        url = self.addr + url

        return self.app.session.request(method, url, *args, headers = headers, **kwargs)

    def post(self, url, payload, headers):
        url = self.addr + url

        return self.app.session.post(url, json = payload, headers = headers)

    async def send(self, message_id, username, msg, created_at):
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username': username,
            'text': msg,
            'gateway': self.gateway
        }

        return await self.post("/api/message", payload, headers)

    # Read message from Matterbridge API stream and pass them to unit3d.send() (IRC -> Chatbox)
    async def watch(self):
        async with self.request("GET", "/api/stream") as req:
            async for msg in self.app.jsonlines(req):
                if msg["text"] != '':
                    username, message = self.app.get_message_attributes(msg, "matterbridgeapi")

                    print(f"(IRC -> Chatbox) [{username}] {message}")
                    self.logger.info(f"(IRC -> Chatbox) [{username}] {message}")

                    await self.app.unit3d.send(msg)
