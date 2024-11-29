from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from user_management.models import User

def send_push_notification(expo_token, title, message):
    try:
        response = PushClient().publish(
            PushMessage(to=expo_token,
                       title=title,
                       body=message)
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

def notify_admins_lesson_completed(lesson, completed_by):
    admins = User.objects.filter(role=User.Role.ADMIN, expo_push_token__isnull=False)
    
    for admin in admins:
        send_push_notification(
            admin.expo_push_token,
            "Lesson Completed",
            f"{completed_by.name} has completed lesson: {lesson.name}"
        )
