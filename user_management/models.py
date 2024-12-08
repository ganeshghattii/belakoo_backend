from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VOLUNTEER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

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
