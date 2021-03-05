#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
import threading 
import config
import dsp

logging.basicConfig()

PORT = 6789
STATE = {
    "color": {
        "r": 255,
        "g": 0,
        "b": 0,
    },
    "frequency": {
        "min": 50,
        "max": 1000,
    },
    "sigma": 4.0
}

USERS = set()


async def message_handler(message):
    data = json.loads(message)
    if data["action"] == "color":
        # TODO check data
        STATE["color"] = data["value"]
        await notify_state()
    elif data["action"] == "frequency":
        # TODO check data
        STATE["frequency"] = data["value"]
        min = int(data["value"]["min"])
        if min < 0:
            min = 0
        max = int(data["value"]["max"])
        if max <= 0:
            max = 1
        config.MIN_FREQUENCY = min
        config.MAX_FREQUENCY = max
        dsp.create_mel_bank()
        await notify_state()
    elif data["action"] == "sigma":
        # TODO check data
        STATE["sigma"] = data["value"]
        await notify_state()
    else:
        logging.error("unsupported event: {}", data)


def state_event():
    return json.dumps({"type": "state", **STATE})


def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def handler(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            await message_handler(message)
    finally:
        await unregister(websocket)

def start_server_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handler, "0.0.0.0", PORT)
    
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

server_thread = threading.Thread(target=start_server_async)
server_thread.start()