import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pusher

pusher_client = pusher.Pusher(
    app_id=os.environ['PUSHER_APP_ID'],
    key=os.environ['PUSHER_KEY'],
    secret=os.environ['PUSHER_SECRET'],
    cluster=os.environ['PUSHER_CLUSTER'],
    ssl=True
)

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'some_group'
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to Pusher
        pusher_client.trigger(self.group_name, 'chat_message', {'message': message})

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
