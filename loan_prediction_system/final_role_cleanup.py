import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_approval_system.settings')
django.setup()

from loan_app.models import User

def final_cleanup():
    # 1. Update all 'user' to 'applicant'
    users_to_update = User.objects.filter(role='user')
    u_count = users_to_update.count()
    for u in users_to_update:
        u.role = 'applicant'
        u.save()
    print(f"Updated {u_count} legacy 'user' roles to 'applicant'.")

    # 2. Ensure only Gnanesh is admin
    admins = User.objects.filter(role='admin').exclude(username='Gnanesh')
    a_count = admins.count()
    for a in admins:
        a.role = 'applicant'
        a.is_staff = False
        a.is_superuser = False
        a.save()
    print(f"Demoted {a_count} extra admins.")

    # 3. Ensure Gnanesh is super admin
    gnanesh = User.objects.get(username='Gnanesh')
    gnanesh.role = 'admin'
    gnanesh.is_staff = True
    gnanesh.is_superuser = True
    gnanesh.save()
    print("Gnanesh is now the sole Super Admin.")

if __name__ == "__main__":
    final_cleanup()
