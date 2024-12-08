import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from user_management.models import User

def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("Firebase already initialized")
    except ValueError:
        # Use credentials from settings
        cred = credentials.Certificate(settings.FIREBASE_ADMIN_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized")

# Initialize Firebase when module loads
initialize_firebase()

def send_push_notification(fcm_token, title, message, data=None):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            data=data or {},
            token=fcm_token,
        )
        
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
        return True
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False

def notify_admins_lesson_completed(lesson, completed_by):
    admins = User.objects.filter(
        role='ADMIN',
        fcm_token__isnull=False
    )
    
    for admin in admins:
        send_push_notification(
            fcm_token=admin.fcm_token,
            title="Lesson Completion Review Required",
            message=f"{completed_by.name} has completed lesson: {lesson.name}",
            data={
                "lesson_id": str(lesson.id),
                "lesson_code": lesson.lesson_code,
                "completed_by_id": str(completed_by.id),
                "notification_type": "lesson_completion"
            }
        )