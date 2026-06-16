import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_approval_system.settings')
django.setup()

from loan_app.models import User

def create_demo_users():
    users_to_create = [
        {'username': 'admin_demo', 'email': 'admin@demo.com', 'password': 'demo_password123', 'role': 'admin', 'first_name': 'System', 'last_name': 'Admin'},
        {'username': 'officer_demo', 'email': 'officer@demo.com', 'password': 'demo_password123', 'role': 'officer', 'first_name': 'Loan', 'last_name': 'Officer'},
        {'username': 'user_demo', 'email': 'user@demo.com', 'password': 'demo_password123', 'role': 'user', 'first_name': 'Normal', 'last_name': 'User'}
    ]

    for u_data in users_to_create:
        if not User.objects.filter(username=u_data['username']).exists():
            user = User.objects.create_user(
                username=u_data['username'],
                email=u_data['email'],
                password=u_data['password'],
                role=u_data['role'],
                first_name=u_data['first_name'],
                last_name=u_data['last_name']
            )
            print(f"Created {u_data['role']} account: {u_data['username']}")
        else:
            print(f"Account {u_data['username']} already exists.")

if __name__ == '__main__':
    create_demo_users()
