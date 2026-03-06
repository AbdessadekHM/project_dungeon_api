import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken #type:ignore
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError #type:ignore
from django.contrib.auth import get_user_model
from .models import Message, Project

User = get_user_model()


def get_user_from_token(token_key):
    try:
        UntypedToken(token_key)
        from rest_framework_simplejwt.backends import TokenBackend #type:ignore
        from django.conf import settings
        data = TokenBackend(
            algorithm='HS256',
            signing_key=settings.SECRET_KEY
        ).decode(token_key, verify=True)
        return User.objects.get(id=data['user_id'])
    except (InvalidToken, TokenError, User.DoesNotExist, Exception):
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'

        query_string = self.scope.get('query_string', b'').decode()
        token = None
        for part in query_string.split('&'):
            if part.startswith('token='):
                token = part[6:]
                break

        if token is None:
            await self.close(code=4001)
            return

        self.user = await database_sync_to_async(get_user_from_token)(token)
        if self.user is None:
            await self.close(code=4001)
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '').strip()
        if not content:
            return

        message = await database_sync_to_async(Message.objects.create)(
            project_id=self.project_id,
            sender=self.user,
            content=content,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'content': content,
                'sender': self.user.username,
                'sender_id': self.user.id,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'content': event['content'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'created_at': event['created_at'],
        }))
