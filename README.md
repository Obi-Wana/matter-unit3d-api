# Matterunit3d

Matterunit3d is a [Matterbridge](https://github.com/42wim/matterbridge)
API plugin (forked from "matteredit 2") allowing you to connect UNIT3D chatbox chats to the various
chat services supported by Matterbridge.

## Features
This reads messages from the Matterbridge API and posts them to UNIT3D chat using a custom API endpoint.
Message flow from IRC -> Chatbox: <br>
IRC -> Matterbridge Bot reads the message and posts it to the Matterbridge API -> Matterunit3d picks up the message and posts it to `https://unit3d.dev/api/chats/messages`.
<br>
A custom API endpoint in UNIT3D must exist in order to receive the messages and forward them to the existing `messages()` function.

## Setup
- Setup Matterbridge on your server (see example config below) as a systemd service
- Clone this repository to a local directory
- Adjust configs and run it as systemd service (or by hand `usr/bin/python3 -m matterunit3d matterunit3d.ini`)

## Example Configuration
### matterbridge.toml

```
[irc]
    [irc.unit3d]
    Server="127.0.0.1:6667"
    Nick="Bot"
    Password="Server Password"
    UseSASL=false
    Charset="utf-8"
    RemoteNickFormat="[{NICK}] "
    RejoinDelay=2
    DebugLevel=1

[api]
    [api.api]
    BindAddress="127.0.0.1:4242"
    Buffer=0
    
[[gateway]]
name="unit3d-irc-sb"
enable=true
inout = [
    { account="irc.unit3d", channel="#<IRCChannel>"},
    { account="api.unit3d", channel="api"},
]

```

Add these to your existing Matterbridge config to set up an API instance
that Mattereddit can connect to.

### matterunit3d.ini

```
[unit3d]
address = https://unit3d.site/
username = Bot
token = <Bot_API_TOken>
chatroom_id = 1

[matterbridge]
address = http://127.0.0.1:4242     # Must match the matterbrdige API bind address
gateway = unit3d-irc-sb             # Must match the matterbridge gateway name
```

## Running as systemd service
````
# cat /etc/systemd/system/matterunit3d.service
[Unit]
Description=Matterbridge UNIT3D Plugin daemon
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m matterunit3d matterunit3d.ini
WorkingDirectory=/.../matter-unit3d-api                         # Path to git repo
Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal
#User=matterbridge

[Install]
WantedBy=multi-user.target
```
