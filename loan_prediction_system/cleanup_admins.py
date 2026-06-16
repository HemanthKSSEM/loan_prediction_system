import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_approval_system.settings')
django.setup()

from loan_app.models import User

def consolidate_admin():
    # Target Admin
    target_username = 'Gnanesh'
    
    # Ensure Gnanesh is Admin
    gnanesh, created = User.objects.get_or_create(username=target_username)
    gnanesh.role = 'admin'
    gnanesh.is_staff = True
    gnanesh.is_superuser = True
    gnanesh.save()
    print(f"Verified {target_username} as the primary Admin.")
    
    # Demote all other Admins
    other_admins = User.objects.filter(role='admin').exclude(username=target_username)
    count = other_admins.count()
    for user in other_admins:
        user.role = 'applicant'
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print(f"Demoted: {user.username}")
    
    print(f"Cleaned up {count} other admin accounts.")

if __name__ == "__main__":
    consolidate_admin()
