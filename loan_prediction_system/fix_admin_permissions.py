import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_approval_system.settings')
django.setup()

from loan_app.models import User

def fix_permissions():
    admins = User.objects.filter(role='admin')
    for admin in admins:
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"Fixed permissions for: {admin.username}")

if __name__ == "__main__":
    fix_permissions()
