import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ForumMessage
from classrooms.models import Classroom
from django.contrib.auth import get_user_model

User = get_user_model()

class ForumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.classroom_id = self.scope['url_route']['kwargs']['classroom_id']
        self.room_group_name = f"classroom_{self.classroom_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'send')

        if msg_type == 'send':
            message = data['message']
            sender_id = data['sender_id']
            forum_message = await self.save_message(sender_id, message, self.classroom_id)
        elif msg_type == 'edit':
            message_id = data['message_id']
            message = data['message']
            sender_id = data['sender_id']
            forum_message = await self.edit_message(message_id, sender_id, message)
        else:
            return    

    
        serialized = await self.serialize_message(forum_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'data': serialized
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def save_message(self, sender_id, message, classroom_id):
        return ForumMessage.objects.create(
            sender=User.objects.get(id=sender_id),
            content=message,
            classroom=Classroom.objects.get(id=classroom_id)
            )
    @database_sync_to_async
    def edit_message(self, message_id, sender_id, new_content):
        try:
            message = ForumMessage.objects.get(id=message_id, sender_id=sender_id)
            message.content = new_content
            message.save()
            return message
        except ForumMessage.DoesNotExist:
            # Optionally handle unauthorized or not found case
            return None

    @database_sync_to_async
    def serialize_message(self, forum_message):
        sender = forum_message.sender
        role = sender.role
        first_name = last_name = None

        if role == "teacher" and hasattr(sender, "teacher_profile"):
            first_name = sender.teacher_profile.first_name
            last_name = sender.teacher_profile.last_name
        elif role == "student" and hasattr(sender, "student_profile"):
            first_name = sender.student_profile.first_name
            last_name = sender.student_profile.last_name

        return {
            "id": forum_message.id,
            "content": forum_message.content,
            "timestamp": forum_message.timestamp.isoformat(),
            "updatedAt": forum_message.updatedAt.isoformat(),
            "classroom": forum_message.classroom.id,
            "sender": {
                "id": sender.id,
                "email": sender.email,
                "firstName": first_name,
                "lastName": last_name,
                "role": sender.role
            }
        }

