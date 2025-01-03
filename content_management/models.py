from django.db import models
import uuid
import json
from django.conf import settings
from user_management.models import User

class Campus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campus_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Campuses"

    def __str__(self):
        return self.name

class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='grades')

    def __str__(self):
        return self.name

class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    icon = models.URLField()
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects')
    colorcode = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Proficiency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proficiency_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='proficiencies')

    class Meta:
        verbose_name_plural = "Proficiencies"

    def __str__(self):
        return self.name

class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson_code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='lessons')
    proficiency = models.ForeignKey(Proficiency, on_delete=models.CASCADE, related_name='lessons')
    is_done = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    completed_by = models.ForeignKey('user_management.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_lessons')
    objective = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=250, null=True, blank=True)
    specific_learning_outcome = models.TextField(null=True, blank=True)
    behavioral_outcome = models.TextField(null=True, blank=True)
    materials_required = models.TextField(null=True, blank=True)
    resources=models.TextField(null=True, blank=True)
    activate = models.JSONField(null=True, blank=True)
    acquire = models.JSONField(null=True, blank=True)
    apply = models.JSONField(null=True, blank=True)
    assess = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.lesson_code
