# Generated by Django 5.1.2 on 2024-10-26 15:18

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('campus_code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.URLField()),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Campuses',
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('grade_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='content_management.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('subject_code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.URLField()),
                ('colorcode', models.CharField(max_length=10)),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='content_management.grade')),
            ],
        ),
        migrations.CreateModel(
            name='Proficiency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('proficiency_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proficiencies', to='content_management.subject')),
            ],
            options={
                'verbose_name_plural': 'Proficiencies',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lesson_code', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_done', models.BooleanField(default=False)),
                ('objective', models.TextField(blank=True, null=True)),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
                ('specific_learning_outcome', models.TextField(blank=True, null=True)),
                ('behavioural_outcome', models.TextField(blank=True, null=True)),
                ('materials_required', models.TextField(blank=True, null=True)),
                ('activate', models.JSONField(blank=True, null=True)),
                ('acquire', models.JSONField(blank=True, null=True)),
                ('apply', models.JSONField(blank=True, null=True)),
                ('assess', models.JSONField(blank=True, null=True)),
                ('proficiency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='content_management.proficiency')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='content_management.subject')),
            ],
        ),
    ]
