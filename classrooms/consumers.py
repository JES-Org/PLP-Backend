# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message, Classroom, MessageReadStatus, Teacher, Student
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.classroom_id = self.scope['url_route']['kwargs']['classroom_id']
        self.room_group_name = f'chat_{self.classroom_id}'
        self.user = self.scope["user"]

        # Add detailed logging
        logger.info(f"WebSocket connection attempt - Classroom: {self.classroom_id}")
        logger.info(f"User type: {type(self.user)}")
        logger.info(f"User authenticated: {self.user.is_authenticated}")
        
        if hasattr(self.user, 'id'):
            logger.info(f"User ID: {self.user.id}, Username: {getattr(self.user, 'username', 'N/A')}")
        else:
            logger.warning("User object has no ID attribute")

        if not self.user.is_authenticated:
            logger.warning("Connection rejected: User not authenticated")
            await self.close()
            return

        try:
            # Verify classroom access
            has_access = await self.verify_classroom_access()
            if not has_access:
                logger.warning(f"User {self.user.id} has no access to classroom {self.classroom_id}")
                await self.close()
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"WebSocket connection accepted for user {self.user.id} in classroom {self.classroom_id}")
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            await self.close()

    @database_sync_to_async
    def verify_classroom_access(self):
        """Verify the user has access to this classroom"""
        from django.core.exceptions import ObjectDoesNotExist
        try:
            classroom = Classroom.objects.get(id=self.classroom_id)
            if self.user.role == 'teacher':
                return classroom.teacher.user == self.user
            elif self.user.role == 'student':
                return classroom.students.filter(user=self.user).exists()
            return False
        except ObjectDoesNotExist:
            return False

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            # Handle new messages
            message_content = data['message']
            message = await self.save_message(
                self.user.id, 
                self.classroom_id, 
                message_content
            )

            # Get user's display name
            display_name = await self.get_user_display_name(self.user)

            # Broadcast message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': display_name,
                    'sender_id': self.user.id,
                    'message_id': message.id,
                    'timestamp': message.timestamp.isoformat(),
                }
            )
        
        elif message_type == 'read_receipt':
            # Handle read receipts
            message_id = data['message_id']
            await self.mark_as_read(message_id, self.user.id)
            
            # Get user's display name
            display_name = await self.get_user_display_name(self.user)

            # Broadcast read receipt to sender
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'reader_id': self.user.id,
                    'reader_name': display_name,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader_id': event['reader_id'],
            'reader_name': event['reader_name'],
        }))

    @database_sync_to_async
    def get_user_display_name(self, user):
        """Get the user's display name based on their role"""
        if user.role == 'teacher':
            teacher = Teacher.objects.filter(user=user).first()
            if teacher:
                return f"{teacher.first_name} {teacher.last_name}"
        elif user.role == 'student':
            student = Student.objects.filter(user=user).first()
            if student:
                return f"{student.first_name} {student.last_name}"
        return user.email 

    @database_sync_to_async
    def save_message(self, user_id, classroom_id, content):  
        user = User.objects.get(id=user_id)
        classroom = Classroom.objects.get(id=classroom_id)
        return Message.objects.create(
            sender=user,
            classroom=classroom,
            content=content
        )

    @database_sync_to_async
    def mark_as_read(self, message_id, user_id):
        obj, created = MessageReadStatus.objects.get_or_create(
            message_id=message_id,
            user_id=user_id,
            defaults={'is_read': True, 'read_at': timezone.now()}
        )
        if not created and not obj.is_read:
            obj.is_read = True
            obj.read_at = timezone.now()
            obj.save()
        return obj
