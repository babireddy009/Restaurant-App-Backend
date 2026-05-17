import asyncio
import websockets
import json
import jwt
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken

user = CustomUser.objects.first()
token = str(AccessToken.for_user(user))

async def test_ws():
    uri = f"ws://localhost:8000/ws/chat/order/17/?token={token}"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            msg = await websocket.recv()
            print("Received:", msg)
            
            await websocket.send(json.dumps({'message': 'Hello from test', 'sender': 'customer'}))
            msg = await websocket.recv()
            print("Received after send:", msg)
    except Exception as e:
        print("WebSocket Error:", e)

asyncio.run(test_ws())
