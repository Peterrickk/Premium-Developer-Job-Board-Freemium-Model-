from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin superuser if it does not exist'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Checking for existing superusers...')
            
            # Check if superuser already exists
            superuser_exists = User.objects.filter(is_superuser=True).exists()
            if superuser_exists:
                self.stdout.write(self.style.SUCCESS('✓ Superuser already exists'))
                return

            # Get credentials from environment variables or use defaults
            username = os.getenv('ADMIN_USERNAME', 'admin')
            email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            password = os.getenv('ADMIN_PASSWORD', 'admin123')

            self.stdout.write(f'Creating superuser with username: {username}')
            
            # Check if user already exists by username
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists, updating to superuser...'))
                user = User.objects.get(username=username)
                user.is_superuser = True
                user.is_staff = True
                user.set_password(password)
                user.save()
            else:
                # Create superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Superuser created successfully!'))

            self.stdout.write(self.style.SUCCESS(
                f'Admin Account Details:\n'
                f'  Username: {username}\n'
                f'  Email: {email}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating superuser: {str(e)}'))
            import traceback
            traceback.print_exc()
            # Don't fail the build if superuser creation fails
            pass

