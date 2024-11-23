from django.core.management.base import BaseCommand
from user_management.models import User

class Command(BaseCommand):
    help = 'Creates the default admin user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email='admin@belakoo.com').exists():
            User.objects.create_user(
                email='admin@belakoo.com',
                password='admin',
                name='Admin',
                role=User.Role.ADMIN,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
