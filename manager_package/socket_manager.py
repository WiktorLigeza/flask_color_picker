import websockets
import json


async def update_tag(key, new_tag, new_name, old_tag):
    url = "wss://hal9000-color-picker-websockserver.glitch.me"
    async with websockets.connect(url) as ws:
        x = {"head": "set", "type": "change_tag",  "TAG": old_tag, "key": key, "NAME": new_name, "NEW_TAG": new_tag}
        data = json.dumps(x)
        print("sending: ", data)
        await ws.send(data)


async def update_connection_key(old_key, new_key, tag):
    url = "wss://hal9000-color-picker-websockserver.glitch.me"
    async with websockets.connect(url) as ws:
        x = {"head": "set", "type": "change_key", "TAG": tag, "key": old_key, "new_key": new_key}
        data = json.dumps(x)
        print("sending: ", data)
        await ws.send(data)