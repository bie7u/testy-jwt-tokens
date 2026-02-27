"""
Management command to seed the database with test users.

Usage:
    python manage.py seed_users

Creates:
  Staff users (intranet):
    - admin / admin123        (superuser)
    - staff1 / staff123       (is_staff)
    - staff2 / staff123       (is_staff)

  Customer users (Frontend 2):
    - customer1 / customer123
    - customer2 / customer123
    - customer3 / customer123
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


STAFF_USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'staff1',
        'password': 'staff123',
        'email': 'staff1@example.com',
        'first_name': 'Staff',
        'last_name': 'One',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'staff2',
        'password': 'staff123',
        'email': 'staff2@example.com',
        'first_name': 'Staff',
        'last_name': 'Two',
        'is_staff': True,
        'is_superuser': False,
    },
]

CUSTOMER_USERS = [
    {
        'username': 'customer1',
        'password': 'customer123',
        'email': 'customer1@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'customer2',
        'password': 'customer123',
        'email': 'customer2@example.com',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'customer3',
        'password': 'customer123',
        'email': 'customer3@example.com',
        'first_name': 'Bob',
        'last_name': 'Johnson',
        'is_staff': False,
        'is_superuser': False,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with test staff and customer users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding users...\n')

        self._create_users(STAFF_USERS, 'Staff')
        self._create_users(CUSTOMER_USERS, 'Customer')

        self.stdout.write(self.style.SUCCESS('\nDone! Seeded users:\n'))
        self.stdout.write('  Staff / Intranet users:\n')
        for u in STAFF_USERS:
            self.stdout.write(f"    {u['username']} / {u['password']}")
        self.stdout.write('\n  Customer users:\n')
        for u in CUSTOMER_USERS:
            self.stdout.write(f"    {u['username']} / {u['password']}")
        self.stdout.write('\n')

    def _create_users(self, users, group_label):
        for data in users:
            username = data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  [SKIP] {group_label} user "{username}" already exists.')
                continue

            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data.get('email', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                is_staff=data.get('is_staff', False),
                is_superuser=data.get('is_superuser', False),
            )
            self.stdout.write(f'  [OK]   {group_label} user "{user.username}" created.')
