from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin superuser if it does not exist'

    def handle(self, *args, **options):
        try:
            # Check if superuser already exists
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write(self.style.SUCCESS('Superuser already exists'))
                return

            # Get credentials from environment variables or use defaults
            username = os.getenv('ADMIN_USERNAME', 'admin')
            email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            password = os.getenv('ADMIN_PASSWORD', 'admin123')

            # Create superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(self.style.SUCCESS(
                f'Superuser created successfully!\n'
                f'Username: {username}\n'
                f'Email: {email}'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create superuser: {str(e)}'))
            # Don't fail the build if superuser creation fails
            pass

