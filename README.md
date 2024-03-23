# Matterunit3d

Matterunit3d is a [Matterbridge](https://github.com/42wim/matterbridge)
API plugin (forked from "matteredit 2") allowing you to connect UNIT3D chatbox chats to the various
chat services supported by Matterbridge.

## Setup
- Setup Matterbridge on your server (see example config below) as a systemd service
- Clone this repository to a local directory
- Adjust configs and run it as systemd service (`/usr/bin/python3 /matter-unit3d-api/matterunit3d.py --config /matter-unit3d-api/matterunit3d.json`)

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

### matterunit3d.json

```
{
    "unit3d":
    {
        "sync_user_id": "1",                                                # ID of the UNIT3D user that posts the messages in UNIT3D chatbox
        "sync_user_username": "Bot",                                        # Username of user used in sync_user_id
        "sync_user_token": "<TOKEN>",                                       # UNIT3D API token of sync_user
        "receive": "https://aither.dev/api/chats/messages/<Chatroom_ID>",   # Endpoint to check for new messages from Chatbox v3
        "send": "https://aither.dev/api/chats/messages",                    # Endpoint to send a new message to Chatbox v3
        "chatroom_id": "1"                                                  # The Chatroom ID (as in the UNIT3D DB)
    },
    "matterbridge":
    {
        "api": "http://127.0.0.1:4242",
        "gateway": "unit3d-irc-sb"
    }
}
```

## Running as systemd service
````
# cat /etc/systemd/system/matterunit3d.service
[Unit]
Description=Matterbridge UNIT3D Plugin daemon
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /matter-unit3d-api/matterunit3d.py --config /matter-unit3d-api/matterunit3d.json
Restart=always
RestartSec=5s
#User=matterbridge

[Install]
WantedBy=multi-user.target
```
