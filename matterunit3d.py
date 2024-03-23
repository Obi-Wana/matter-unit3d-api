import argparse
import json
import requests
import syslog
import threading
import time
import traceback

from datetime import datetime, timedelta


# ARGS
def parse_arguments():
    parser = argparse.ArgumentParser(description="matterunit3d script")
    parser.add_argument("--config", required=True, help="Path to the configuration JSON file")
    return parser.parse_args()
args = parse_arguments()
with open(args.config) as f:
    config = json.load(f)

# UNIT3D
unit3d_sync_user_id = config["unit3d"]["sync_user_id"]
unit3d_user = config["unit3d"]["sync_user_username"]
unit3d_api_key = config["unit3d"]["sync_user_token"]
unit3d_send_api_endpoint = config["unit3d"]["send"]
unit3d_receive_api_endpoint = config["unit3d"]["receive"]
unit3d_receiving_room = config["unit3d"]["chatroom_id"]

# MB API
sess = requests.Session()
if "token" in config["matterbridge"]:
    sess.headers["Authorization"] = "Bearer " + config["matterbridge"]["token"]
mb_api = config["matterbridge"]["api"]
mb_gateway = config["matterbridge"]["gateway"]

# Variable to store IDs or timestamps of processed messages
processed_messages = set()

# Logging
syslog.openlog(ident='matterunit3d', logoption=syslog.LOG_PID)


# Read message in UNIT3D chatbox
def read_messages_unit3d():
    try:
        url_receive = (f"{unit3d_receive_api_endpoint}?api_token={unit3d_api_key}")
        response = sess.get(url_receive)
        response.raise_for_status()
        messages = response.json()["data"]
        return messages
    except Exception as e:
        print("Error fetching messages:", e)
        return []

# Send message to UNIT3D API
def send_message_unit3d(text, message, username):
    # text = message without username prefix
    print(f"[IRC -> Chatbox] New message '{text}' sent by user '{username}'")
    syslog.syslog(f"[IRC -> Chatbox] New message '{text}' sent by user '{username}'")

    try:
        payload = {
            'username': username,
            'message': message,
            'chatroom_id': unit3d_receiving_room,
            'save': 'true',
            'targeted': '0',
            'user_id': unit3d_sync_user_id
        }
        url_send = (f"{unit3d_send_api_endpoint}?api_token={unit3d_api_key}")
        sess.post(url_send, json=payload)
    except Exception as e:
        print("Error sending message:", e)

# Send message to Matterbridge API
def send_message_matterbrige_api(message, username):
    print(f"[Chatbox -> IRC] New message '{message}' sent by user '{username}'")
    syslog.syslog(f"[Chatbox -> IRC] New message '{message}' sent by user '{username}'")
    
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'username': username,
            'text': message,
            'gateway': 'ath-irc-sb'
        }
        response = sess.post(mb_api + "/api/message", json=data, headers=headers)
    except Exception as e:
        print("Error sending message to matterbrdige API: ", e)

# Check UNIT3D chatbox for new messages and send them to IRC (via matterbridge API)
def process_messages_unit3d():
    while True:
        try:
            messages = read_messages_unit3d()
            for msg in messages:
                message_id = msg['id']
                username = msg["username"]
                text = msg["message"]
                created_at = datetime.strptime(msg['created_at'], '%Y-%m-%d %H:%M:%S')

                # Check if the message was sent before OR if it is older than the last check
                # and prevent the bot from bridging its own messages
                if username != unit3d_user and message_id not in processed_messages:
                    if created_at < datetime.now() - timedelta(seconds=15):
                        processed_messages.add(message_id)
                    else:
                        send_message_matterbrige_api(text, username)
                        processed_messages.add(message_id)
        except Exception as e:
            traceback.print_exc()
        time.sleep(2)

# Check IRC channel for new messages and send them to UNIT3D chatbox (via matterbridge API)
def process_messages_matterbridge_api():
    url = mb_api + '/api/stream'
    try:
        response = sess.get(url, stream=True)
        for line in response.iter_lines():
            if line:
                data = json.loads(line)

                username = data.get("username", "")
                text = data.get("text", "")
                message = add_username_to_irc_message(text, username)
                created_at = data.get("timestamp", "")
                
                if text != "":
                    send_message_unit3d(text, message, username)
    except Exception as e:
        print("Error processing stream messages:", e)
        traceback.print_exc()

def add_username_to_irc_message(text, username):
    print(text, username)
    return (f'[{username}] {text}')

def watch_unit3d():
    while True:
        try:
            process_messages_unit3d()
        except Exception as e:
            print("Error in watch_unit3d():", e)
            traceback.print_exc()
        break

def watch_matterbrdige_api():
    while True:
        try:
            process_messages_matterbridge_api()
        except Exception as e:
            print("Error in watch_matterbrdige_api():", e)
            traceback.print_exc()
        break

threading.Thread(target=watch_unit3d).start()
threading.Thread(target=watch_matterbrdige_api).start()
