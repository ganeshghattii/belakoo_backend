# Generated by Django 5.1.2 on 2024-11-29 17:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0004_rename_behavioural_outcome_lesson_behavioral_outcome'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='completed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_lessons', to=settings.AUTH_USER_MODEL),
        ),
    ]
