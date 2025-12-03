from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from work.models import UserProfile


class Command(BaseCommand):
    help = 'Ensure admin user exists with administrator type'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for admin user (default: admin123)'
        )
    
    def handle(self, *args, **options):
        password = options['password']
        
        try:
            # Check if admin user exists
            if not User.objects.filter(username='admin').exists():
                # Create admin user
                admin_user = User.objects.create_user(
                    username='admin',
                    email='admin@example.com',
                    password=password
                )
                # Get or create user profile and set as administrator
                user_profile, created = UserProfile.objects.get_or_create(user=admin_user)
                user_profile.user_type = 'admin'
                user_profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS('Default admin user created successfully')
                )
                self.stdout.write(f'Username: admin')
                self.stdout.write(f'Password: {password}')
                self.stdout.write('User type: Administrator')
            else:
                # Ensure existing admin user has administrator type
                admin_user = User.objects.get(username='admin')
                user_profile, created = UserProfile.objects.get_or_create(user=admin_user)
                if user_profile.user_type != 'admin':
                    user_profile.user_type = 'admin'
                    user_profile.save()
                    self.stdout.write(
                        self.style.SUCCESS('Admin user type updated to administrator')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('Admin user already exists with administrator type')
                    )
                
                # Update password if provided
                if password != 'admin123':
                    admin_user.set_password(password)
                    admin_user.save()
                    self.stdout.write('Admin user password updated')
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {e}')
            )