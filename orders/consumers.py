import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_order_{self.order_id}'
        self.user = self.scope['user']

        # Accept connection
        await self.accept()

        # Check authentication and authorization
        is_authorized = await self.is_authorized()
        if not self.user.is_authenticated or not is_authorized:
            await self.close(code=4003) # Forbidden
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Send previous messages
        messages = await self.get_previous_messages()
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender_role = text_data_json.get('sender', 'customer')

        if message:
            # Save message to database
            sender_name = self.user.get_full_name() or self.user.username
            sender = f"{sender_name}|{sender_role}"
            
            msg_obj = await self.save_message(sender, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'timestamp': msg_obj.timestamp.isoformat()
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def is_authorized(self):
        try:
            order = Order.objects.get(id=self.order_id)
            if not self.user.is_authenticated:
                return False
            # Allow the customer who placed the order, staff members, or the assigned driver
            return order.user == self.user or getattr(self.user, 'role', None) in ('admin', 'staff') or order.driver == self.user
        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def get_previous_messages(self):
        messages = ChatMessage.objects.filter(order_id=self.order_id).order_by('timestamp')
        return [
            {
                'id': msg.id,
                'message': msg.message,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    @database_sync_to_async
    def save_message(self, sender, message):
        return ChatMessage.objects.create(
            order_id=self.order_id,
            sender=sender,
            message=message
        )
