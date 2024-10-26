from django.db import models
import uuid
import json

class Campus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campus_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    icon = models.URLField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Campuses"

    def __str__(self):
        return self.name

class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    icon = models.URLField()
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='subjects')
    colorcode=models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')

    def __str__(self):
        return self.name

class Proficiency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proficiency_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='proficiencies')

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
    objective = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True)
    specific_learning_outcome = models.TextField(null=True, blank=True)
    behavioural_outcome = models.TextField(null=True, blank=True)
    materials_required = models.TextField(null=True, blank=True)
    activate = models.JSONField(null=True, blank=True)
    acquire = models.JSONField(null=True, blank=True)
    apply = models.JSONField(null=True, blank=True)
    assess = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.lesson_code
