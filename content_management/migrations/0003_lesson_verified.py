# Generated by Django 5.1.2 on 2024-11-23 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0002_remove_campus_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
