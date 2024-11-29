import requests
import json
from django.conf import settings
from user_management.models import User

def send_push_notification(expo_push_token, title, message, data=None):
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "to": expo_push_token,
        "sound": "default",
        "title": title,
        "body": message,
        "data": data or {},
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Notification sent successfully to {expo_push_token}")
        else:
            print(f"Failed to send notification: {response.content}")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

def notify_admins_lesson_completed(lesson, completed_by):
    # Get all admins with push tokens
    admins = User.objects.filter(
        role='admin',  # adjust based on your role field
        expo_push_token__isnull=False
    )
    
    for admin in admins:
        send_push_notification(
            expo_push_token=admin.expo_push_token,
            title="Lesson Completion Review Required",
            message=f"{completed_by.full_name} has completed lesson: {lesson.name}",
            data={
                "lesson_id": str(lesson.id),
                "lesson_code": lesson.lesson_code,
                "completed_by_id": str(completed_by.id),
                "notification_type": "lesson_completion"
            }
        )
