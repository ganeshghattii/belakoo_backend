# Generated by Django 5.1.2 on 2024-12-14 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0008_lesson_resources'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='subject_code',
            field=models.CharField(max_length=10),
        ),
    ]