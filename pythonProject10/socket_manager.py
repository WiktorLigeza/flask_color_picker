import websockets
import json


async def update_tag(tag):
    print("sending:", tag)
    url = "wss://hal9000-color-picker-websockserver.glitch.me"
    async with websockets.connect(url) as ws:
        x = {"rPi_TAG": tag}
        data = json.dumps(x)
        await ws.send(data)
