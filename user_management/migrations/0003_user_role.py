# Generated by Django 5.1.2 on 2024-11-23 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_alter_user_options_remove_user_created_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('VOLUNTEER', 'Volunteer')], default='VOLUNTEER', max_length=20),
        ),
    ]
