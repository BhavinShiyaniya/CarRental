from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from car.models import Notification, NotificationGroup

class NotificationConsumer(AsyncWebsocketConsumer):
    '''send notification message to car owner'''

    async def connect(self):
        print("Websocket Connection open...")
        # self.group_name = 'notification'
        self.group_name = self.scope['user'].username

        # join to group
        # await self.channel_layer.group_add(self.group_name, self.channel_name)

        if self.scope['user'].is_hostuser:
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()

    async def disconnect(self):
        print("Websocket Connection closed...")

        # leave group
        await self.channel_layer.group_discard(self.group_name,
                                               self.channel_name)
        
    # Receive message from websocket
    async def receive(self, text_data):
        print("Message Received...",text_data)

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        event = {
            'type': 'send.message',
            'message': message
        }

        # send message to group
        await self.channel_layer.group_send(self.group_name, event)

    # Receive message from group
    async def send_message(self, event):
        message = event['message']

        # send message to websocket
        await self.send(text_data=json.dumps({'message': message}))
