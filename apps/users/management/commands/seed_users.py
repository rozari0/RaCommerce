from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    """A command to seed user into DB"""

    help = "Seeds Dummy User in Database"

    def handle(self, *args, **options):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        print(f"Created superuser: {admin.username} ({admin.email})")

        for i in range(5):
            user = User.objects.create_user(
                username=f"user{i + 1}",
                email=f"user{i + 1}@example.com",
                password="user123",
            )
            print(f"Created user: {user.username} ({user.email})")
