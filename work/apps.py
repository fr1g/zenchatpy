from django.apps import AppConfig


class WorkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'work'
    
    def ready(self):
        """Ensure admin user exists when app starts"""
        try:
            from django.contrib.auth.models import User
            from .models import UserProfile
            
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_user(
                    username='admin',
                    email='admin@adm.in',
                    password='admin123'
                )
                user_profile, created = UserProfile.objects.get_or_create(user=admin_user)
                user_profile.user_type = 'admin'
                user_profile.save()
                print(f"Default admin user created: {created}")
            else:
                admin_user = User.objects.get(username='admin')
                user_profile, created = UserProfile.objects.get_or_create(user=admin_user)
                if user_profile.user_type != 'admin':
                    user_profile.user_type = 'admin'
                    user_profile.save()
                    print("Admin user type updated to administrator")
        except Exception as e:
            print(f"Error ensuring admin: {e}")
