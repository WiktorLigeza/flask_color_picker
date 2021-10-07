import websockets
import json


async def update_tag(new_tag, new_name, old_tag):
    url = "wss://hal9000-color-picker-websockserver.glitch.me"
    async with websockets.connect(url) as ws:
        x = {"device_tag": old_tag, "NAME": new_name, "NEW_TAG": new_tag}
        data = json.dumps(x)
        print("sending: ", data)
        await ws.send(data)


async def update_connection_key(new_key):
    url = "wss://hal9000-color-picker-websockserver.glitch.me"
    async with websockets.connect(url) as ws:
        x = {"key": new_key}
        data = json.dumps(x)
        print("sending: ", data)
        await ws.send(data)