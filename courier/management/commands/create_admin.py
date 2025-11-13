from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courier.models import UserProfile
import os


class Command(BaseCommand):
    help = 'Create admin superuser if it does not exist'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@courier.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not User.objects.filter(username=username).exists():
            # Create superuser
            user = User.objects.create_superuser(username, email, password)

            # Create admin profile
            UserProfile.objects.create(
                user=user,
                role='admin',
                phone='',
                address='System Administrator'
            )

            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully with admin role!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists.')
            )
